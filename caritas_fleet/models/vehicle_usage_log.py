from odoo import models, fields

class VehicleUsageLog(models.Model):
    _name = 'vehicle.usage.log'
    _description = 'Vehicle Usage Log'

    vehicle_id = fields.Many2one('fleet.vehicle', string='Vehicle', required=True)
    trip_id = fields.Many2one('vehicle.trip', string='Trip')
    start_datetime = fields.Datetime(string='Start Date')
    end_datetime = fields.Datetime(string='End Date')
    mileage = fields.Float(string='Mileage')
    vehicle_department_id = fields.Many2one('vehicle.department', string='Department', related='vehicle_id.vehicle_department_id', store=True)
