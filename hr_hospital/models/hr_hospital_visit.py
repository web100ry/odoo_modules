from odoo import fields, models


class HrHospitalVisit(models.Model):
    _name = 'hr.hospital.visit'
    _description = 'Patient Visit'

    patient_id = fields.Many2one(comodel_name='hr.hospital.patient',  required=True)
    doctor_id = fields.Many2one(comodel_name='hr.hospital.doctor',  required=True)
    visit_date = fields.Datetime(default=fields.Datetime.now)
    notes = fields.Text()
