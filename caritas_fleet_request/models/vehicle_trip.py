from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class VehicleTrip(models.Model):
    _name = "vehicle.trip"
    _description = "Vehicle Trip"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "date_start desc, id desc"
    _rec_name = "calendar_display_name"

    name = fields.Char(string="Trip", default="New", copy=False, readonly=True)
    request_id = fields.Many2one("vehicle.request", string="Vehicle Request", ondelete="set null")
    requester_id = fields.Many2one(
        comodel_name="res.users",
        string="Requester",
        default=lambda self: self.env.user,
        required=True,
    )
    department_id = fields.Many2one(
        comodel_name="vehicle.department",
        string="Department",
    )
    vehicle_id = fields.Many2one(
        comodel_name="fleet.vehicle",
        string="Vehicle",
        required=True,
    )
    driver_id = fields.Many2one(
        comodel_name="res.users",
        string="Driver",
        domain=lambda self: [
            (
                "groups_id",
                "in",
                self.env.ref("caritas_fleet_request.group_fleet_driver", raise_if_not_found=False).ids
                or [],
            )
        ],
    )
    date_start = fields.Datetime(string="Start Date", required=True)
    date_end = fields.Datetime(string="End Date", required=True)

    request_state = fields.Selection(
        related="request_id.state",
        string="Request Status",
        readonly=True,
    )

    calendar_event_id = fields.Many2one(
        comodel_name="calendar.event",
        string="Calendar Event",
        readonly=True,
        ondelete="set null",
        copy=False,
    )

    calendar_display_name = fields.Char(
        string="Calendar Title",
        compute="_compute_calendar_display_name",
    )

    @api.model
    def create(self, vals):
        if vals.get("name", "New") == "New":
            vals["name"] = self.env["ir.sequence"].next_by_code("vehicle.trip") or "New"
        if not vals.get("department_id") and vals.get("vehicle_id"):
            vehicle = self.env["fleet.vehicle"].browse(vals["vehicle_id"])
            vals["department_id"] = vehicle.department_id.id or False
        trips = super().create(vals)
        trips._sync_calendar_event(create_if_missing=True)
        return trips

    def write(self, vals):
        if vals.get("vehicle_id") and not vals.get("department_id"):
            vehicle = self.env["fleet.vehicle"].browse(vals["vehicle_id"])
            vals = dict(vals, department_id=vehicle.department_id.id or False)
        relevant_fields = {"date_start", "date_end", "driver_id", "vehicle_id", "requester_id", "department_id", "name"}
        res = super().write(vals)
        if relevant_fields.intersection(vals) or self.filtered("calendar_event_id"):
            self._sync_calendar_event(create_if_missing=True)
        return res

    def unlink(self):
        events = self.calendar_event_id
        if events:
            events.with_context(from_vehicle_trip=True).unlink()
        return super().unlink()

    @api.constrains("date_start", "date_end")
    def _check_dates(self):
        for trip in self:
            if trip.date_start and trip.date_end and trip.date_end <= trip.date_start:
                raise ValidationError(_("End Date must be after Start Date."))

    @api.depends(
        "requester_id",
        "driver_id",
        "vehicle_id",
        "vehicle_id.model_id",
        "vehicle_id.model_id.brand_id",
        "request_state",
    )
    def _compute_calendar_display_name(self):
        for trip in self:
            trip.calendar_display_name = trip._build_calendar_event_name()

    def _build_calendar_event_name(self):
        self.ensure_one()

        requester = None
        if self._fields.get("requester_id"):
            requester = self.requester_id
        elif self._fields.get("user_id"):
            requester = self.user_id
        requester_partner = requester.partner_id if requester else False

        name_tokens = (requester_partner.name or "") if requester_partner else ""
        parts = [part for part in name_tokens.split() if part]
        last_name = parts[0] if parts else ""
        initials = ".".join(token[0].upper() for token in parts[1:] if token)
        if initials:
            initials = f"{initials}."
        requester_part = " ".join(filter(None, [last_name, initials])).strip()

        brand = self.vehicle_id.model_id.brand_id.name if self.vehicle_id and self.vehicle_id.model_id else ""
        model_name = self.vehicle_id.model_id.name if self.vehicle_id and self.vehicle_id.model_id else ""
        vehicle_name = " ".join(filter(None, [brand, model_name]))
        license_plate = self.vehicle_id.license_plate or ""
        vehicle_part = ", ".join(filter(None, [vehicle_name, license_plate]))

        if requester_part and vehicle_part:
            base_title = f"{requester_part} — {vehicle_part}"
        else:
            base_title = requester_part or vehicle_part or _("Trip")

        state_icons = {
            "draft": "🟢",
            "approved": "✅",
            "in_progress": "🚗",
            "done": "✔️",
            "closed": "🔒",
            "rejected": "⛔️",
        }
        icon = state_icons.get(self.request_state)
        if icon:
            return f"{icon} {base_title}"
        return base_title

    def _prepare_calendar_event_values(self):
        self.ensure_one()
        if not self.date_start or not self.date_end:
            return None

        requester = None
        if self._fields.get("requester_id"):
            requester = self.requester_id
        elif self._fields.get("user_id"):
            requester = self.user_id

        partner_ids = []
        if requester and requester.partner_id:
            partner_ids.append(requester.partner_id.id)

        owner = self.driver_id if self._fields.get("driver_id") and self.driver_id else requester or self.env.user

        return {
            "name": self._build_calendar_event_name(),
            "start": self.date_start,
            "stop": self.date_end,
            "user_id": owner.id if owner else False,
            "partner_ids": [(6, 0, partner_ids)],
            "vehicle_trip_id": self.id,
        }

    def _sync_calendar_event(self, create_if_missing=True):
        CalendarEvent = self.env["calendar.event"]
        for trip in self:
            values = trip._prepare_calendar_event_values()
            if not values:
                continue
            if trip.calendar_event_id:
                trip.calendar_event_id.with_context(from_vehicle_trip=True).write(values)
            elif create_if_missing:
                event = CalendarEvent.create(values)
                trip.calendar_event_id = event.id
