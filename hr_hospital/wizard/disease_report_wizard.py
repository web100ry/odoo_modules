from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class DiseaseReportWizard(models.TransientModel):
    _name = 'disease.report.wizard'
    _description = 'Disease Report Wizard'

    doctor_ids = fields.Many2many(
        comodel_name='hr.hospital.doctor',
        string='Doctors',
        help='Leave empty to include all doctors',
    )

    disease_ids = fields.Many2many(
        comodel_name='hr.hospital.disease',
        string='Diseases',
        help='Leave empty to include all diseases',
    )

    country_ids = fields.Many2many(
        comodel_name='res.country',
        string='Countries',
        help='Filter by patient citizenship',
    )

    date_from = fields.Date(
        string='Date From',
        required=True,
        default=fields.Date.context_today,
    )

    date_to = fields.Date(
        string='Date To',
        required=True,
        default=fields.Date.context_today,
    )

    report_type = fields.Selection(
        selection=[
            ('detailed', 'Detailed'),
            ('summary', 'Summary'),
        ],
        string='Report Type',
        default='summary',
        required=True,
    )

    group_by = fields.Selection(
        selection=[
            ('doctor', 'Doctor'),
            ('disease', 'Disease'),
            ('month', 'Month'),
            ('country', 'Country'),
        ],
        string='Group By',
        default='disease',
    )

    @api.constrains('date_from', 'date_to')
    def _check_dates(self):
        """Ensure date_from is before date_to"""
        for wizard in self:
            if wizard.date_from > wizard.date_to:
                raise ValidationError(
                    _("'Date From' must be earlier than 'Date To'!")
                )

    def action_generate_report(self):
        """Generate disease report based on criteria"""
        self.ensure_one()

        # Build domain for diagnoses
        domain = [
            ('visit_id.planned_datetime', '>=', fields.Datetime.to_datetime(self.date_from)),
            ('visit_id.planned_datetime', '<=', fields.Datetime.to_datetime(self.date_to)),
        ]

        if self.doctor_ids:
            domain.append(('visit_id.doctor_id', 'in', self.doctor_ids.ids))

        if self.disease_ids:
            domain.append(('disease_id', 'in', self.disease_ids.ids))

        if self.country_ids:
            domain.append(('visit_id.patient_id.country_id', 'in', self.country_ids.ids))

        # Search diagnoses
        diagnoses = self.env['hr.hospital.medical.diagnosis'].search(domain)

        if not diagnoses:
            raise ValidationError(
                _("No diagnoses found for the selected criteria!")
            )

        # Generate report data
        if self.report_type == 'detailed':
            report_data = self._generate_detailed_report(diagnoses)
        else:
            report_data = self._generate_summary_report(diagnoses)

        # Return tree view with results
        return {
            'name': _('Disease Report'),
            'type': 'ir.actions.act_window',
            'res_model': 'hr.hospital.medical.diagnosis',
            'view_mode': 'tree,form',
            'domain': [('id', 'in', diagnoses.ids)],
            'context': {
                'default_report_data': report_data,
            }
        }

    def _generate_detailed_report(self, diagnoses):
        """Generate detailed report data"""
        data = []
        for diagnosis in diagnoses:
            data.append({
                'diagnosis': diagnosis.name,
                'disease': diagnosis.disease_id.name if diagnosis.disease_id else '',
                'doctor': diagnosis.visit_id.doctor_id.name,
                'patient': diagnosis.visit_id.patient_id.name,
                'country': diagnosis.visit_id.patient_id.country_id.name if diagnosis.visit_id.patient_id.country_id else '',
                'date': diagnosis.visit_id.planned_datetime,
                'severity': dict(diagnosis._fields['severity'].selection).get(diagnosis.severity, ''),
            })
        return data

    def _generate_summary_report(self, diagnoses):
        """Generate summary report data"""
        data = {}

        if self.group_by == 'doctor':
            for diagnosis in diagnoses:
                doctor = diagnosis.visit_id.doctor_id
                if doctor.id not in data:
                    data[doctor.id] = {
                        'name': doctor.name,
                        'count': 0,
                        'diseases': set(),
                    }
                data[doctor.id]['count'] += 1
                if diagnosis.disease_id:
                    data[doctor.id]['diseases'].add(diagnosis.disease_id.name)

        elif self.group_by == 'disease':
            for diagnosis in diagnoses:
                disease = diagnosis.disease_id
                disease_key = disease.id if disease else 0
                disease_name = disease.name if disease else _('Unspecified')

                if disease_key not in data:
                    data[disease_key] = {
                        'name': disease_name,
                        'count': 0,
                        'doctors': set(),
                    }
                data[disease_key]['count'] += 1
                data[disease_key]['doctors'].add(diagnosis.visit_id.doctor_id.name)

        elif self.group_by == 'month':
            for diagnosis in diagnoses:
                month_key = diagnosis.visit_id.planned_datetime.strftime('%Y-%m')
                if month_key not in data:
                    data[month_key] = {
                        'name': month_key,
                        'count': 0,
                    }
                data[month_key]['count'] += 1

        elif self.group_by == 'country':
            for diagnosis in diagnoses:
                country = diagnosis.visit_id.patient_id.country_id
                country_key = country.id if country else 0
                country_name = country.name if country else _('Unspecified')

                if country_key not in data:
                    data[country_key] = {
                        'name': country_name,
                        'count': 0,
                    }
                data[country_key]['count'] += 1

        return list(data.values())
