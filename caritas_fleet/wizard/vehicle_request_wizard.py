from odoo import models, fields, api

class VehicleRequestWizard(models.TransientModel):
    _name = 'vehicle.request.wizard'
    _description = 'Vehicle Request Wizard'

    requester_id = fields.Many2one('res.users', string='Requester', default=lambda self: self.env.user, required=True)
    request_type = fields.Selection([
        ('with_driver', 'With Driver'),
        ('self_drive', 'Self Drive')
    ], string='Request Type', required=True, default='with_driver')
    vehicle_id = fields.Many2one('fleet.vehicle', string='Vehicle')
    driver_id = fields.Many2one('res.users', string='Driver')
    start_datetime = fields.Datetime(string='Start Date', required=True)
    end_datetime = fields.Datetime(string='End Date', required=True)

    def action_create_request(self):
        self.ensure_one()
        vals = {
            'requester_id': self.requester_id.id,
            'request_type': self.request_type,
            'vehicle_id': self.vehicle_id.id,
            'driver_id': self.driver_id.id,
            'start_datetime': self.start_datetime,
            'end_datetime': self.end_datetime,
            'state': 'draft',
        }
        request = self.env['vehicle.request'].create(vals)
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'vehicle.request',
            'res_id': request.id,
            'view_mode': 'form',
            'target': 'current',
        }
