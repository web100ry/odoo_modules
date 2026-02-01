from odoo import fields, models, _
from odoo.exceptions import ValidationError


class VehicleTripDateFilterWizard(models.TransientModel):
    _name = "vehicle.trip.date.filter.wizard"
    _description = "Trip Date Filter"

    date_from = fields.Datetime(string="Date From", required=True)
    date_to = fields.Datetime(string="Date To", required=True)
    department_id = fields.Many2one("vehicle.department", string="Department")
    vehicle_id = fields.Many2one("fleet.vehicle", string="Vehicle")

    def action_apply_filter(self):
        self.ensure_one()
        if self.date_to <= self.date_from:
            raise ValidationError(_("End date must be after start date."))

        domain = [
            ("date_start", ">=", self.date_from),
            ("date_end", "<=", self.date_to),
        ]

        if self.department_id:
            domain.append(("department_id", "=", self.department_id.id))
        if self.vehicle_id:
            domain.append(("vehicle_id", "=", self.vehicle_id.id))

        return {
            "type": "ir.actions.act_window",
            "res_model": "vehicle.trip",
            "view_mode": "list,calendar",
            "domain": domain,
            "target": "current",
        }