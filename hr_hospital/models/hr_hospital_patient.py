from odoo import models, fields


class HrHospitalPatient(models.Model):
    _name = 'hr.hospital.patient'
    _description = 'Patient'

    name = fields.Char()
    age = fields.Integer()
    gender = fields.Selection(
        selection=[('male', 'Male'), ('female', 'Female')])
    disease_id = fields.Many2one('hr.hospital.disease')
    doctor_id = fields.Many2one('hr.hospital.doctor')
