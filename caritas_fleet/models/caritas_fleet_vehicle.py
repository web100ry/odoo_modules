from odoo import models, fields, api

class CaritasFleetVehicle(models.Model):
    _name = 'caritas.fleet.vehicle'
    _inherit = ['fleet.vehicle', 'mail.thread', 'mail.activity.mixin']
    _description = 'Caritas Fleet Vehicle'

    caritas_id = fields.Char(string='Caritas ID', tracking=True)
