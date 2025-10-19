from odoo import models, fields


class HrHospital(models.Model):
    _name = 'hr.hospital'
    _description = 'Hospital'

    id = fields.Integer(string='ID')
    name = fields.Char(string='Name')
    address = fields.Integer(string='Address')
    branchid = fields.Char(string='Branchid')
    description = fields.Text()
    hospital_id = fields.Many2one('hr.hospital', string='Hospital')