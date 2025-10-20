from odoo import models, fields


class HrHospitalPatient(models.Model):
    _name = 'hr.hospital.patient'
    _description = 'Patient'

   # id = fields.Integer(integer='ID')
    name = fields.Char(string='FullName')
    age = fields.Integer(string='Age')
    gender = fields.Selection([('male', 'Male'), ('female', 'Female')], string='Gender')
    disease_id = fields.Many2one('hr.hospital.disease', string='Disease')
    doctor_id = fields.Many2one('hr.hospital.doctor', string='Doctor')