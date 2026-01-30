from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class VehicleRequestRejectWizard(models.TransientModel):
    _name = "vehicle.request.reject.wizard"
    _description = "Vehicle Request Rejection Wizard"

    request_id = fields.Many2one(
        comodel_name="vehicle.request",
        string="Request",
        required=True,
    )

    comment = fields.Text(
        string="Comment",
        required=True,
    )

    def action_confirm(self):
        self.ensure_one()
        request = self.request_id

        if request.state != "done":
            raise ValidationError(_("Only completed requests can be rejected at this stage."))

        if request.vehicle_id and request.vehicle_id.availability_status == "reserved":
            request.vehicle_id.availability_status = "available"

        request.state = "rejected"

        admin_group = self.env.ref("caritas_fleet_request.group_fleet_admin", raise_if_not_found=False)
        admin_partners = admin_group.users.partner_id if admin_group else self.env["res.partner"]

        body = (
            "<p><strong>%s</strong></p><p>%s</p><p><a href='#' data-oe-model='vehicle.request' "
            "data-oe-id='%s'>%s</a></p>"
            % (
                _("Request rejected"),
                self.comment,
                request.id,
                request.display_name,
            )
        )

        request.message_post(
            body=body,
            subtype_xmlid="mail.mt_note",
            partner_ids=admin_partners.ids,
        )

        return {"type": "ir.actions.act_window_close"}