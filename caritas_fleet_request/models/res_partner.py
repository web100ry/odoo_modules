from odoo import models


class ResPartner(models.Model):
    _inherit = "res.partner"

    def name_get(self):
        if self.env.context.get("caritas_org_format"):
            result = []
            for partner in self:
                commercial_partner = partner.commercial_partner_id or partner
                base_name = commercial_partner.name or partner.commercial_company_name or partner.name or ""
                city = commercial_partner.city or partner.city or ""
                if city and base_name:
                    display = f"{city}, {base_name}"
                else:
                    display = base_name or city
                result.append((partner.id, display))
            return result
        return super().name_get()
