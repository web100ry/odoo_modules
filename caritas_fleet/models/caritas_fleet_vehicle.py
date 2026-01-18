from odoo import models, fields, api

class CaritasFleetVehicle(models.Model):
    _name = 'caritas.fleet.vehicle'
    _inherit = ['fleet.vehicle', 'mail.thread', 'mail.activity.mixin']
    _description = 'Caritas Fleet Vehicle'

    caritas_id = fields.Char(string='Caritas ID', tracking=True)
    tag_ids = fields.Many2many(
        'fleet.vehicle.tag',
        'caritas_fleet_vehicle_tag_rel',
        'vehicle_id',
        'tag_id',
        string='Tags',
        copy=False
    )
