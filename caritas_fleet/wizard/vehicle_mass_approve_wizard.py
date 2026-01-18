from odoo import models, fields, api

class VehicleMassApproveWizard(models.TransientModel):
    _name = 'vehicle.mass.approve.wizard'
    _description = 'Mass Approve Vehicle Requests'

    request_ids = fields.Many2many('vehicle.request', string='Requests', domain=[('state', '=', 'draft')])

    def action_mass_approve(self):
        self.request_ids.action_approve()
        return {'type': 'ir.actions.act_window_close'}

    def action_mass_reject(self):
        self.request_ids.action_reject()
        return {'type': 'ir.actions.act_window_close'}
