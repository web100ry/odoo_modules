from odoo import api, fields, models, _
from odoo.exceptions import UserError


class VehicleRequestBulkApproveWizard(models.TransientModel):
    _name = "vehicle.request.bulk.approve.wizard"
    _description = "Bulk Approve Vehicle Requests"

    request_ids = fields.Many2many(
        comodel_name="vehicle.request",
        string="Requests",
        readonly=True,
    )

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        active_ids = self.env.context.get("active_ids") or []
        if active_ids:
            res["request_ids"] = [(6, 0, active_ids)]
        return res

    def action_bulk_approve(self):
        self.ensure_one()
        requests = self.request_ids
        if not requests:
            return {"type": "ir.actions.act_window_close"}

        non_draft = requests.filtered(lambda r: r.state != "draft")
        if non_draft:
            raise UserError(_("All selected requests must be in draft state."))

        requests.action_approve()

        return {
            "type": "ir.actions.act_window",
            "res_model": "vehicle.request",
            "view_mode": "list,form",
            "target": "main",
        }