from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class VehicleRequest(models.Model):
    _name = "vehicle.request"
    _description = "Vehicle Request"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    name = fields.Char(
        string="Request Reference",
        readonly=True,
        copy=False,
        default="New",
    )

    requester_id = fields.Many2one(
        comodel_name="res.users",
        string="Requester",
        default=lambda self: self.env.user,
        readonly=True,
    )

    department_id = fields.Many2one(
        comodel_name="vehicle.department",
        string="Department",
        default=lambda self: self._default_department(),
    )

    trip_type = fields.Selection(
        selection=[
            ("with_driver", "With Driver"),
            ("self_drive", "Self Drive"),
        ],
        string="Trip Type",
        default="with_driver",
        required=True,
    )

    vehicle_id = fields.Many2one(
        comodel_name="fleet.vehicle",
        string="Vehicle",
        domain=[("availability_status", "=", "available")],
    )

    driver_id = fields.Many2one(
        comodel_name="res.users",
        string="Driver",
        domain=lambda self: [
            (
                "groups_id",
                "in",
                self.env.ref(
                    "caritas_fleet_request.group_fleet_driver",
                    raise_if_not_found=False,
                ).ids
                or [],
            )
        ],
    )

    date_start = fields.Datetime(
        string="Start Date",
        required=True,
    )

    date_end = fields.Datetime(
        string="End Date",
        required=True,
    )

    state = fields.Selection(
        selection=[
            ("draft", "New"),
            ("approved", "Approved"),
            ("in_progress", "In Progress"),
            ("done", "Completed"),
            ("closed", "Closed"),
            ("rejected", "Rejected"),
        ],
        string="Status",
        default="draft",
        tracking=True,
    )

    @api.model
    def create(self, vals):
        if vals.get("name", "New") == "New":
            vals["name"] = self.env["ir.sequence"].next_by_code("vehicle.request") or "New"
        return super().create(vals)

    @api.model
    def _default_department(self):
        return self.env["vehicle.department"].search(
            [("user_ids", "in", self.env.user.id)],
            limit=1,
        )

    @api.constrains("date_start", "date_end")
    def _check_dates(self):
        for request in self:
            if request.date_start and request.date_end and request.date_end <= request.date_start:
                raise ValidationError(_("End Date must be after Start Date."))

    @api.onchange("department_id")
    def _onchange_department_id(self):
        domain = [("availability_status", "=", "available")]
        if self.department_id:
            domain.append(("department_id", "=", self.department_id.id))
        else:
            domain.append(("department_id", "=", False))
        return {"domain": {"vehicle_id": domain}}

    def action_approve(self):
        for request in self:
            if request.state != "draft":
                raise ValidationError(_("Only draft requests can be approved."))
            if not request.vehicle_id:
                raise ValidationError(_("A vehicle must be selected before approval."))
            if request.trip_type == "with_driver" and not request.driver_id:
                raise ValidationError(_("Driver is required for trips with driver."))
            if request.trip_type == "self_drive" and request.driver_id:
                raise ValidationError(_("Driver must be empty for self-drive trips."))
            if request.vehicle_id.availability_status != "available":
                raise ValidationError(_("Only available vehicles can be approved."))
            request.state = "approved"
            request.vehicle_id.availability_status = "reserved"
        return True

    def action_reject(self):
        for request in self:
            if request.vehicle_id and request.vehicle_id.availability_status == "reserved":
                request.vehicle_id.availability_status = "available"
            request.state = "rejected"
        return True

    def action_start(self):
        for request in self:
            if request.state != "approved":
                raise ValidationError(_("Only approved requests can be started."))
            if request.trip_type == "with_driver" and not request.driver_id:
                raise ValidationError(_("Driver is required to start this trip."))
            request.state = "in_progress"
        return True

    def action_done(self):
        for request in self:
            if request.state != "in_progress":
                raise ValidationError(_("Only in-progress requests can be completed."))
            request.state = "done"
        return True

    def action_close(self):
        for request in self:
            if request.state != "done":
                raise ValidationError(_("Only completed requests can be closed."))
            request.state = "closed"
            if request.vehicle_id:
                request.vehicle_id.availability_status = "available"
        return True

    def action_open_reject_wizard(self):
        self.ensure_one()
        if self.state != "done":
            raise ValidationError(_("Only completed requests can be rejected at this stage."))

        return {
            "name": _("Vehicle Request Rejection"),
            "type": "ir.actions.act_window",
            "res_model": "vehicle.request.reject.wizard",
            "view_mode": "form",
            "target": "new",
            "context": {
                "default_request_id": self.id,
            },
        }