import json
import csv
import io
import base64
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class PatientCardExportWizard(models.TransientModel):
    _name = 'patient.card.export.wizard'
    _description = 'Patient Card Export Wizard'

    patient_id = fields.Many2one(
        comodel_name='hr.hospital.patient',
        required=True,
    )

    date_from = fields.Date()

    date_to = fields.Date()

    include_diagnoses = fields.Boolean(
        default=True,
    )

    include_recommendations = fields.Boolean(
        default=True,
    )

    lang_id = fields.Many2one(
        comodel_name='res.lang',
    )

    export_format = fields.Selection(
        selection=[
            ('json', 'JSON'),
            ('csv', 'CSV'),
        ],
        default='json',
        required=True,
    )

    # Export result fields
    export_file = fields.Binary(
        readonly=True,
    )

    export_filename = fields.Char(
        string='Filename',
        readonly=True,
    )

    @api.model
    def default_get(self, fields_list):
        """Set default values from context"""
        res = super().default_get(fields_list)

        # Get patient_id from context
        if self.env.context.get('active_model') == 'hr.hospital.patient':
            patient_id = self.env.context.get('active_id')
            if patient_id:
                res['patient_id'] = patient_id
                # Set default language to patient's language
                patient = self.env['hr.hospital.patient'].browse(patient_id)
                if patient.lang_id:
                    res['lang_id'] = patient.lang_id.id

        return res

    @api.constrains('date_from', 'date_to')
    def _check_dates(self):
        """Ensure date_from is before date_to"""
        for wizard in self:
            if wizard.date_from and wizard.date_to:
                if wizard.date_from > wizard.date_to:
                    raise ValidationError(
                        _("'Date From' must be earlier than 'Date To'!")
                    )

    def action_export(self):
        """Export patient medical card"""
        self.ensure_one()

        if not self.patient_id:
            raise ValidationError(_("Please select a patient!"))

        # Collect patient data
        patient_data = self._collect_patient_data()

        # Export to selected format
        if self.export_format == 'json':
            file_content, filename = self._export_to_json(patient_data)
        else:
            file_content, filename = self._export_to_csv(patient_data)

        # Save file data
        self.write({
            'export_file': base64.b64encode(file_content),
            'export_filename': filename,
        })

        # Return download action
        return {
            'type': 'ir.actions.act_url',
            'url': '/web/content/patient.card.export.wizard/%s/export_file/%s?download=true' % (
                self.id, filename
            ),
            'target': 'self',
        }

    def _collect_patient_data(self):
        """Collect patient medical card data"""
        patient = self.patient_id

        # Basic patient information
        data = {
            'patient_name': patient.name,
            'birth_date': patient.birth_date.isoformat() if patient.birth_date else None,
            'age': patient.age,
            'gender': patient.gender,
            'phone': patient.phone,
            'email': patient.email,
            'country': patient.country_id.name if patient.country_id else None,
            'passport_data': patient.passport_data,
            'blood_type': dict(patient._fields['blood_type'].selection).get(patient.blood_type, ''),
            'allergies': patient.allergies,
            'personal_doctor': patient.personal_doctor_id.name if patient.personal_doctor_id else None,
            'insurance_company': patient.insurance_company_id.name if patient.insurance_company_id else None,
            'insurance_policy_number': patient.insurance_policy_number,
        }

        # Build domain for visits
        domain = [('patient_id', '=', patient.id)]

        if self.date_from:
            domain.append(('planned_datetime', '>=', fields.Datetime.to_datetime(self.date_from)))

        if self.date_to:
            domain.append(('planned_datetime', '<=', fields.Datetime.to_datetime(self.date_to)))

        # Get visits
        visits = self.env['hr.hospital.visit'].search(domain, order='planned_datetime desc')

        visits_data = []
        for visit in visits:
            visit_info = {
                'date': visit.planned_datetime.isoformat() if visit.planned_datetime else None,
                'doctor': visit.doctor_id.name,
                'visit_type': dict(visit._fields['visit_type'].selection).get(visit.visit_type, ''),
                'status': dict(visit._fields['status'].selection).get(visit.status, ''),
            }

            # Include recommendations if requested
            if self.include_recommendations and visit.recommendations:
                visit_info['recommendations'] = visit.recommendations

            # Include diagnoses if requested
            if self.include_diagnoses:
                diagnoses_data = []
                for diagnosis in visit.diagnosis_ids:
                    diagnosis_info = {
                        'name': diagnosis.name,
                        'disease': diagnosis.disease_id.name if diagnosis.disease_id else None,
                        'description': diagnosis.description,
                        'severity': dict(diagnosis._fields['severity'].selection).get(diagnosis.severity, ''),
                        'approved': diagnosis.approved,
                    }
                    if diagnosis.treatment:
                        diagnosis_info['treatment'] = diagnosis.treatment
                    diagnoses_data.append(diagnosis_info)

                visit_info['diagnoses'] = diagnoses_data

            visits_data.append(visit_info)

        data['visits'] = visits_data
        data['visits_count'] = len(visits_data)

        return data

    def _export_to_json(self, data):
        """Export data to JSON format"""
        json_content = json.dumps(data, indent=2, ensure_ascii=False)
        filename = 'patient_card_%s_%s.json' % (
            self.patient_id.id,
            fields.Date.today().isoformat()
        )
        return json_content.encode('utf-8'), filename

    def _export_to_csv(self, data):
        """Export data to CSV format"""
        output = io.StringIO()

        # Write patient basic info
        writer = csv.writer(output)
        writer.writerow(['Patient Medical Card'])
        writer.writerow([])
        writer.writerow(['Patient Information'])
        writer.writerow(['Name', data.get('patient_name', '')])
        writer.writerow(['Birth Date', data.get('birth_date', '')])
        writer.writerow(['Age', data.get('age', '')])
        writer.writerow(['Gender', data.get('gender', '')])
        writer.writerow(['Phone', data.get('phone', '')])
        writer.writerow(['Email', data.get('email', '')])
        writer.writerow(['Country', data.get('country', '')])
        writer.writerow(['Blood Type', data.get('blood_type', '')])
        writer.writerow(['Allergies', data.get('allergies', '')])
        writer.writerow(['Personal Doctor', data.get('personal_doctor', '')])
        writer.writerow([])

        # Write visits
        writer.writerow(['Visits History'])
        writer.writerow(
            ['Date',
             'Doctor',
             'Type',
             'Status',
             'Recommendations']
        )

        for visit in data.get('visits', []):
            writer.writerow([
                visit.get('date', ''),
                visit.get('doctor', ''),
                visit.get('visit_type', ''),
                visit.get('status', ''),
                visit.get('recommendations', ''),
            ])

            # Write diagnoses for this visit
            if self.include_diagnoses and visit.get('diagnoses'):
                writer.writerow([])
                writer.writerow(
                    ['',
                     'Diagnosis',
                     'Disease',
                     'Severity',
                     'Description']
                )
                for diagnosis in visit.get('diagnoses', []):
                    writer.writerow([
                        '',
                        diagnosis.get('name', ''),
                        diagnosis.get('disease', ''),
                        diagnosis.get('severity', ''),
                        diagnosis.get('description', ''),
                    ])
                writer.writerow([])

        filename = 'patient_card_%s_%s.csv' % (
            self.patient_id.id,
            fields.Date.today().isoformat()
        )

        return output.getvalue().encode('utf-8'), filename
