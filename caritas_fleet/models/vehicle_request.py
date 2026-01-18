from odoo import models, fields, api, _

class VehicleRequest(models.Model):
    _name = 'vehicle.request'
    _description = 'Vehicle Request'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'id desc'

    name = fields.Char(
        string='Reference',
        required=True,
        copy=False,
        readonly=True,
        default=lambda self: _('New')
    )
    requester_id = fields.Many2one(
        'res.users',
        string='Requester',
        default=lambda self: self.env.user,
        required=True,
        tracking=True
    )
    request_type = fields.Selection([
        ('with_driver', 'With Driver'),
        ('self_drive', 'Self Drive')
    ], string='Request Type', required=True, default='with_driver', tracking=True)
    vehicle_id = fields.Many2one(
        'fleet.vehicle',
        string='Vehicle',
        tracking=True
    )
    driver_id = fields.Many2one(
        'res.users',
        string='Driver',
        tracking=True
    )
    start_datetime = fields.Datetime(string='Start Date', required=True, tracking=True)
    end_datetime = fields.Datetime(string='End Date', required=True, tracking=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected')
    ], string='Status', default='draft', tracking=True)
    vehicle_department_id = fields.Many2one(
        'vehicle.department',
        string='Department',
        related='requester_id.vehicle_department_id',
        store=True,
        readonly=True
    )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _('New')) == _('New'):
                vals['name'] = self.env['ir.sequence'].next_by_code('vehicle.request') or _('New')
        return super().create(vals_list)

    def action_approve(self):
        self.write({'state': 'approved'})

    def action_reject(self):
        self.write({'state': 'rejected'})
