from odoo import models, fields, api


class HrHospitalPatientDoctorHistory(models.Model):
    _name = 'hr.hospital.patient.doctor.history'
    _description = 'Patient Doctor History'
    _order = 'assign_date desc'

    patient_id = fields.Many2one(
        comodel_name='hr.hospital.patient',
        required=True,
        ondelete='cascade'
    )

    doctor_id = fields.Many2one(
        comodel_name='hr.hospital.doctor',
        required=True,
        ondelete='restrict'
    )

    assign_date = fields.Date(
        required=True,
        default=fields.Date.context_today
    )

    change_date = fields.Date()
    reason_change = fields.Text()
    notes = fields.Text()
    active = fields.Boolean(default=True)


    @api.model
    def create(self, vals):
        patient_id = vals.get('patient_id')
        if patient_id:
            self.search([('patient_id', '=', patient_id), ('active', '=', True)]).write({'active': False})

        return super().create(vals)