from odoo import models, fields, _
from odoo.exceptions import ValidationError


class CalendarEvent(models.Model):
    _inherit = "calendar.event"

    vehicle_trip_id = fields.Many2one(
        comodel_name="vehicle.trip",
        string="Vehicle Trip",
        ondelete="set null",
        readonly=True,
        index=True,
    )

    def write(self, vals):
        protected_fields = {
            "start",
            "start_datetime",
            "stop",
            "stop_datetime",
            "name",
            "partner_ids",
            "user_id",
        }
        if (
            not self.env.context.get("from_vehicle_trip")
            and protected_fields.intersection(vals)
            and self.filtered("vehicle_trip_id")
        ):
            raise ValidationError(_("You cannot modify a calendar event linked to a vehicle trip manually."))
        return super().write(vals)

    def unlink(self):
        if not self.env.context.get("from_vehicle_trip") and self.filtered("vehicle_trip_id"):
            raise ValidationError(_("You cannot delete a calendar event linked to a vehicle trip manually."))
        return super().unlink()
