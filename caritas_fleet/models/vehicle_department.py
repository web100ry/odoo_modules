from odoo import models, fields

class VehicleDepartment(models.Model):
    _name = 'vehicle.department'
    _description = 'Vehicle Department'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Name', required=True, tracking=True)
    member_ids = fields.One2many('res.users', 'vehicle_department_id', string='Members')
    vehicle_ids = fields.One2many('fleet.vehicle', 'vehicle_department_id', string='Vehicles')

    _sql_constraints = [
        ('name_unique', 'unique(name)', 'Department name must be unique!')
    ]
