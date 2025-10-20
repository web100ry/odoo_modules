from odoo import api, fields, models, _

class HrHospitalVisit(models.Model):
    _name = 'hr.hospital.visit'
    _description = 'Patient Visit'

    patient_id = fields.Many2one('hr.hospital.patient', string='Patient', required=True)
    doctor_id = fields.Many2one('hr.hospital.doctor', string='Doctor', required=True)
    visit_date = fields.Datetime(string='Visit Date', default=fields.Datetime.now)
    notes = fields.Text(string='Notes')
