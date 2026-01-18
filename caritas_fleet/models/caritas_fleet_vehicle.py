from odoo import models, fields

class FleetVehicle(models.Model):
    _inherit = 'fleet.vehicle'

    vehicle_department_id = fields.Many2one(
        'vehicle.department',
        string='Department',
        tracking=True
    )
    responsible_driver_id = fields.Many2one(
        'res.users',
        string='Responsible Driver',
        tracking=True
    )
    availability_state = fields.Selection([
        ('available', 'Available'),
        ('busy', 'Busy'),
        ('maintenance', 'Maintenance')
    ], string='Availability Status', default='available', tracking=True)
