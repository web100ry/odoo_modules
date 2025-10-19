from odoo import models, fields


class HrHospitalDoctor(models.Model):
    _name = 'hr.hospital.doctor'
    _description = 'Doctor'

    id = fields.Integer(string='ID')
    name = fields.Char(string='FullName')
    age = fields.Integer(string='Age')
    gender = fields.Selection([('male', 'Male'), ('female', 'Female')], string='Gender')
    speciality = fields.Char(string='Speciality')
    description = fields.Text()
    hospital_id = fields.Many2one('hr.hospital', string='Hospital')