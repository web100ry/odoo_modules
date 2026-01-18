from odoo import models, fields, api

class SignalConfig(models.Model):
    _name = 'signal.config'
    _description = 'Signal Configuration'

    api_token = fields.Char(string='API Token', required=True)
    is_active = fields.Boolean(string='Is Active', default=False)
    last_sync = fields.Datetime(string='Last Sync')
    message_log = fields.Text(string='Message Log')

    @api.model
    def get_config(self):
        return self.search([], limit=1) or self.create({'api_token': 'default'})
