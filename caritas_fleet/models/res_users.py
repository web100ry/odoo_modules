from odoo import models, fields

class ResUsers(models.Model):
    _inherit = 'res.users'

    is_driver = fields.Boolean(string='Is Driver', default=False)
    vehicle_department_id = fields.Many2one(
        'vehicle.department',
        string='Department'
    )
    driver_license_number = fields.Char(string='Driver License Number')
