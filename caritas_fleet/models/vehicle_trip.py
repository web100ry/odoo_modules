from odoo import models, fields, api

class VehicleTrip(models.Model):
    _name = 'vehicle.trip'
    _description = 'Vehicle Trip'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    request_id = fields.Many2one('vehicle.request', string='Request', required=True)
    vehicle_id = fields.Many2one('fleet.vehicle', string='Vehicle', related='request_id.vehicle_id', store=True)
    driver_id = fields.Many2one('res.users', string='Driver', related='request_id.driver_id', store=True)
    route = fields.Text(string='Route')
    actual_start = fields.Datetime(string='Actual Start')
    actual_end = fields.Datetime(string='Actual End')
    calendar_event_id = fields.Many2one('calendar.event', string='Calendar Event', readonly=True)

    @api.model_create_multi
    def create(self, vals_list):
        trips = super().create(vals_list)
        for trip in trips:
            trip._create_calendar_event()
        return trips

    def _create_calendar_event(self):
        self.ensure_one()
        event_vals = {
            'name': f"Trip: {self.vehicle_id.name or ''} - {self.driver_id.name or ''}",
            'start': self.request_id.start_datetime,
            'stop': self.request_id.end_datetime,
            'description': self.route,
            'user_id': self.driver_id.id or self.env.user.id,
        }
        event = self.env['calendar.event'].create(event_vals)
        self.calendar_event_id = event.id
