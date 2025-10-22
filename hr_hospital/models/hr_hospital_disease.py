from odoo import fields, models


class HrHospitalDisease(models.Model):
    _name = 'hr.hospital.disease'
    _description = 'Disease'

    name = fields.Char()
    description = fields.Text()
