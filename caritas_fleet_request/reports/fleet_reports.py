from odoo import models, _
from odoo.exceptions import ValidationError

from ..wizard.fleet_report_period_wizard import _prepare_trip_search_domain


class ReportVehicleTrips(models.AbstractModel):
    _name = "report.caritas_fleet_request.report_vehicle_trips"
    _description = "Vehicle Trips Report"

    def _get_report_values(self, docids, data=None):
        data = data or {}
        if not data.get("vehicle_id"):
            raise ValidationError(_("Vehicle is required."))

        values = _prepare_trip_search_domain(data, self.env)
        trips = values.get("trips")

        return {
            "doc_ids": trips.ids,
            "doc_model": "vehicle.trip",
            "trips": trips,
            "vehicle": values.get("vehicle"),
            "department": values.get("department"),
            "date_from": values.get("date_from"),
            "date_to": values.get("date_to"),
            "total_trips": len(trips),
            "report_title": _("Vehicle Trips Report"),
        }


class ReportDepartmentTrips(models.AbstractModel):
    _name = "report.caritas_fleet_request.report_department_trips"
    _description = "Department Trips Report"

    def _get_report_values(self, docids, data=None):
        data = data or {}
        if not data.get("department_id"):
            raise ValidationError(_("Department is required."))

        values = _prepare_trip_search_domain(data, self.env)
        trips = values.get("trips")

        return {
            "doc_ids": trips.ids,
            "doc_model": "vehicle.trip",
            "trips": trips,
            "vehicle": values.get("vehicle"),
            "department": values.get("department"),
            "date_from": values.get("date_from"),
            "date_to": values.get("date_to"),
            "total_trips": len(trips),
            "report_title": _("Department Trips Report"),
        }