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

    origin_organization_id = fields.Many2one(
        comodel_name="res.partner",
        string="Departure Organization",
        default=lambda self: self.env.user.partner_id.commercial_partner_id,
    )

    destination_organization_ids = fields.Many2many(
        comodel_name="res.partner",
        string="Destination Organizations",
    )

    origin_city = fields.Char(
        string="Departure City",
        compute="_compute_city_fields",
        readonly=True,
    )

    destination_cities = fields.Char(
        string="Destination Cities",
        compute="_compute_city_fields",
        readonly=True,
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

    trip_category = fields.Selection(
        selection=[
            ("work", "Work"),
            ("business_trip", "Business Trip"),
            ("personal", "Personal"),
        ],
        string="Trip Purpose",
        default="work",
        required=True,
    )

    vehicle_id = fields.Many2one(
        comodel_name="fleet.vehicle",
        string="Vehicle",
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

    trip_details = fields.Text(
        string="Trip Details",
    )

    trip_id = fields.Many2one(
        comodel_name="vehicle.trip",
        string="Trip",
        readonly=True,
        copy=False,
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
        request = super().create(vals)
        request._sync_draft_trip()
        request._notify_fleet_base_new_request()
        return request

    def _notify_fleet_base_new_request(self):
        fleet_base_channel = self.env.ref('caritas_fleet_request.channel_fleet_base', raise_if_not_found=False)
        if not fleet_base_channel:
            return
        for request in self:
            message = _("New vehicle request created: %s") % request.name
            fleet_base_channel.message_post(
                body=message,
                message_type='comment',
                subtype_xmlid='mail.mt_comment'
            )

    def _notify_parties(self, message, notify_requester=False, notify_driver=False, notify_admin=False):
        for request in self:
            partner_ids = []
            if notify_requester and request.requester_id:
                partner_ids.append(request.requester_id.partner_id.id)
            if notify_driver and request.driver_id:
                partner_ids.append(request.driver_id.partner_id.id)
            if notify_admin:
                admin_group = self.env.ref("caritas_fleet_request.group_fleet_admin", raise_if_not_found=False)
                if admin_group:
                    partner_ids.extend(admin_group.users.mapped('partner_id').ids)

            if partner_ids:
                request.message_post(
                    body=message,
                    message_type='comment',
                    subtype_xmlid='mail.mt_comment',
                    partner_ids=list(set(partner_ids))
                )

    def write(self, vals):
        res = super().write(vals)
        draft_requests = self.filtered(lambda r: r.state == "draft")
        if draft_requests:
            draft_requests._sync_draft_trip()
        return res

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

    @api.depends(
        "origin_organization_id.city",
        "origin_organization_id.commercial_partner_id.city",
        "destination_organization_ids.city",
        "destination_organization_ids.commercial_partner_id.city",
    )
    def _compute_city_fields(self):
        for request in self:
            origin_partner = request.origin_organization_id.commercial_partner_id or request.origin_organization_id
            request.origin_city = origin_partner.city or request.origin_organization_id.city or False

            dest_cities = []
            for partner in request.destination_organization_ids:
                commercial = partner.commercial_partner_id or partner
                city = commercial.city or partner.city
                if city:
                    dest_cities.append(city)

            seen = set()
            unique_cities = []
            for city in dest_cities:
                if city not in seen:
                    seen.add(city)
                    unique_cities.append(city)

            request.destination_cities = ", ".join(unique_cities)

    @api.onchange("department_id")
    def _onchange_department_id(self):
        domain = []
        if self.department_id:
            domain.append(("department_id", "=", self.department_id.id))
        else:
            domain.append(("department_id", "=", False))
        return {"domain": {"vehicle_id": domain}}

    def _sync_draft_trip(self):
        for request in self:
            if request.state != "draft":
                continue

            if request.vehicle_id and request.date_start and request.date_end:
                trip_vals = {
                    "request_id": request.id,
                    "requester_id": request.requester_id.id,
                    "department_id": request.department_id.id,
                    "vehicle_id": request.vehicle_id.id,
                    "driver_id": request.driver_id.id if request.driver_id else False,
                    "date_start": request.date_start,
                    "date_end": request.date_end,
                }
                if request.trip_id:
                    request.trip_id.write(trip_vals)
                else:
                    request.trip_id = self.env["vehicle.trip"].create(trip_vals)
            else:
                if request.trip_id:
                    request.trip_id.unlink()
                    request.trip_id = False

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
            overlap_domain = [
                ("vehicle_id", "=", request.vehicle_id.id),
                ("date_start", "<", request.date_end),
                ("date_end", ">", request.date_start),
            ]
            if request.trip_id:
                overlap_domain.append(("id", "!=", request.trip_id.id))
            conflicting_trips = self.env["vehicle.trip"].search(overlap_domain, limit=1)
            if conflicting_trips:
                raise ValidationError(
                    _(
                        "Vehicle %s is already scheduled for the selected period."
                    )
                    % (request.vehicle_id.display_name,)
                )
            trip_vals = {
                "request_id": request.id,
                "requester_id": request.requester_id.id,
                "department_id": request.department_id.id,
                "vehicle_id": request.vehicle_id.id,
                "driver_id": request.driver_id.id if request.driver_id else False,
                "date_start": request.date_start,
                "date_end": request.date_end,
            }
            if request.trip_id:
                request.trip_id.write(trip_vals)
            else:
                request.trip_id = self.env["vehicle.trip"].create(trip_vals)
            request.state = "approved"
            request.vehicle_id.availability_status = "reserved"
            request._notify_parties(
                _("Your vehicle request %s has been approved.") % request.name,
                notify_requester=True,
                notify_driver=True
            )
        return True

    def action_reject(self):
        for request in self:
            if request.vehicle_id and request.vehicle_id.availability_status == "reserved":
                request.vehicle_id.availability_status = "available"
            if request.trip_id:
                request.trip_id.unlink()
                request.trip_id = False
            request.state = "rejected"
            request._notify_parties(
                _("Your vehicle request %s has been rejected.") % request.name,
                notify_requester=True,
                notify_driver=True
            )
        return True

    def action_start(self):
        for request in self:
            if request.state != "approved":
                raise ValidationError(_("Only approved requests can be started."))
            if request.trip_type == "with_driver" and not request.driver_id:
                raise ValidationError(_("Driver is required to start this trip."))
            request.state = "in_progress"
            request._notify_parties(
                _("The trip for request %s has started.") % request.name,
                notify_requester=True,
                notify_admin=True
            )
        return True

    def action_done(self):
        for request in self:
            if request.state != "in_progress":
                raise ValidationError(_("Only in-progress requests can be completed."))
            request.state = "done"
            request._notify_parties(
                _("The trip for request %s has been completed.") % request.name,
                notify_requester=True,
                notify_admin=True
            )
        return True

    def action_close(self):
        for request in self:
            if request.state != "done":
                raise ValidationError(_("Only completed requests can be closed."))
            request.state = "closed"
            if request.vehicle_id:
                request.vehicle_id.availability_status = "available"
            request._notify_parties(
                _("Requester has accepted the work for request %s.") % request.name,
                notify_driver=True,
                notify_admin=True
            )
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