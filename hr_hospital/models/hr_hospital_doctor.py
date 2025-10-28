from odoo import models, fields

class HrHospitalDoctor(models.Model):
    _name = 'hr.hospital.doctor'
    _description = 'Doctor'
    _inherit = ['hr.hospital.abstract.person']

    age = fields.Integer()
    gender = fields.Selection(
        selection=[('male', 'Male'), ('female', 'Female')])
    speciality = fields.Char()
    description = fields.Text()
    hospital_id = fields.Many2one(comodel_name='hr.hospital.hospital')
