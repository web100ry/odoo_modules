from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class MassReassignDoctorWizard(models.TransientModel):
    _name = 'mass.reassign.doctor.wizard'
    _description = 'Mass Reassign Doctor Wizard'

    old_doctor_id = fields.Many2one(
        comodel_name='hr.hospital.doctor',
        string='Old Doctor',
    )

    new_doctor_id = fields.Many2one(
        comodel_name='hr.hospital.doctor',
        string='New Doctor',
        required=True,
    )

    patient_ids = fields.Many2many(
        comodel_name='hr.hospital.patient',
        string='Patients',
        domain="[('personal_doctor_id', '=', old_doctor_id)]",
    )

    change_date = fields.Date(
        string='Change Date',
        default=fields.Date.context_today,
        required=True,
    )

    reason_change = fields.Text(
        string='Reason for Change',
        required=True,
    )

    @api.onchange('old_doctor_id')
    def _onchange_old_doctor_id(self):
        """Update patient domain and clear selection when old doctor changes"""
        if self.old_doctor_id:
            patients = self.env['hr.hospital.patient'].search([
                ('personal_doctor_id', '=', self.old_doctor_id.id)
            ])
            self.patient_ids = patients
            return {
                'domain': {
                    'patient_ids': [('personal_doctor_id', '=', self.old_doctor_id.id)]
                }
            }
        else:
            self.patient_ids = False
            return {
                'domain': {
                    'patient_ids': [('id', '=', False)]
                }
            }

    @api.constrains('old_doctor_id', 'new_doctor_id')
    def _check_different_doctors(self):
        """Ensure old and new doctors are different"""
        for wizard in self:
            if wizard.old_doctor_id and wizard.new_doctor_id:
                if wizard.old_doctor_id.id == wizard.new_doctor_id.id:
                    raise ValidationError(
                        _("Old doctor and new doctor must be different!")
                    )

    def action_reassign(self):
        """Reassign patients to new doctor"""
        self.ensure_one()

        if not self.patient_ids:
            raise ValidationError(_("Please select at least one patient to reassign!"))

        # Update patients with new doctor
        for patient in self.patient_ids:
            patient.write({
                'personal_doctor_id': self.new_doctor_id.id,
            })

            # Create history record
            self.env['hr.hospital.patient.doctor.history'].create({
                'patient_id': patient.id,
                'doctor_id': self.new_doctor_id.id,
                'change_date': self.change_date,
                'reason_change': self.reason_change,
            })

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Success'),
                'message': _('%s patient(s) have been reassigned to %s') % (
                    len(self.patient_ids),
                    self.new_doctor_id.name
                ),
                'type': 'success',
                'sticky': False,
            }
        }
