from odoo import models, api, _
from odoo.exceptions import ValidationError


class ResPartner(models.Model):
    _inherit = 'res.partner'

    @api.constrains('email')
    def _check_unique_email(self):
        for partner in self:
            if not partner.email:
                continue
            duplicate = self.search([
                ('email', '=ilike', partner.email),
                ('id', '!=', partner.id)
            ], limit=1)
            if duplicate:
                raise ValidationError(_("A partner with the email '%s' "
                                        "already exists. "
                                      "Duplicate emails "
                                        "are not allowed.") % partner.email)
