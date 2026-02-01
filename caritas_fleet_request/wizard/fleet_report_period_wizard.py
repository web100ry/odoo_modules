from datetime import date, datetime, time

from dateutil.relativedelta import relativedelta

from odoo import fields, models, _
from odoo.exceptions import ValidationError


class FleetReportPeriodWizard(models.TransientModel):
    _name = "fleet.report.period.wizard"
    _description = "Fleet Report Period Wizard"

    date_from = fields.Date(string="Start Date", required=True, default=lambda self: self._default_date_from())
    date_to = fields.Date(string="End Date", required=True, default=lambda self: self._default_date_to())
    vehicle_id = fields.Many2one("fleet.vehicle", string="Vehicle")
    department_id = fields.Many2one("vehicle.department", string="Department")

    @staticmethod
    def _default_date_range():
        today = date.today()
        first_day_this_month = today.replace(day=1)
        last_day_previous_month = first_day_this_month - relativedelta(days=1)
        first_day_previous_month = last_day_previous_month.replace(day=1)
        return first_day_previous_month, last_day_previous_month

    @classmethod
    def _default_date_from(cls):
        return cls._default_date_range()[0]

    @classmethod
    def _default_date_to(cls):
        return cls._default_date_range()[1]

    def _validate_dates(self):
        for wizard in self:
            if wizard.date_from and wizard.date_to and wizard.date_to < wizard.date_from:
                raise ValidationError(_("End date must be on or after start date."))

    def _prepare_common_data(self):
        self._validate_dates()
        self.ensure_one()
        return {
            "date_from": self.date_from,
            "date_to": self.date_to,
        }

    def action_print_vehicle(self):
        self.ensure_one()
        if not self.vehicle_id:
            raise ValidationError(_("Vehicle is required."))

        data = self._prepare_common_data()
        data.update({
            "vehicle_id": self.vehicle_id.id,
            "report_mode": "vehicle",
        })

        return self.env.ref("caritas_fleet_request.report_vehicle_trips").report_action(self, data=data)

    def action_print_department(self):
        self.ensure_one()
        if not self.department_id:
            raise ValidationError(_("Department is required."))

        data = self._prepare_common_data()
        data.update({
            "department_id": self.department_id.id,
            "report_mode": "department",
        })

        return self.env.ref("caritas_fleet_request.report_department_trips").report_action(self, data=data)


def _prepare_trip_search_domain(data, env):
    date_from = data.get("date_from")
    date_to = data.get("date_to")
    dt_start = datetime.combine(date_from, time.min)
    dt_end = datetime.combine(date_to, time.max)

    domain = [
        ("date_start", ">=", dt_start),
        ("date_end", "<=", dt_end),
    ]

    report_mode = data.get("report_mode")
    vehicle = None
    department = None

    if report_mode == "vehicle":
        vehicle_id = data.get("vehicle_id")
        vehicle = env["fleet.vehicle"].browse(vehicle_id)
        domain.append(("vehicle_id", "=", vehicle.id))
    elif report_mode == "department":
        department_id = data.get("department_id")
        department = env["vehicle.department"].browse(department_id)
        domain.append(("department_id", "=", department.id))

    trips = env["vehicle.trip"].search(domain, order="date_start asc")

    return {
        "trips": trips,
        "vehicle": vehicle,
        "department": department,
        "date_from": date_from,
        "date_to": date_to,
    }