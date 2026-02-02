from odoo import models, _
from odoo.exceptions import ValidationError

from ..wizard.fleet_report_period_wizard import _prepare_trip_search_domain


class ReportVehicleTrips(models.AbstractModel):
    _name = "report.caritas_fleet_request.report_vehicle_trips_template"
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
            "_": _,
        }


class ReportDepartmentTrips(models.AbstractModel):
    _name = "report.caritas_fleet_request.report_department_trips_template"
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
            "_": _,
        }


class ReportPersonnelTrips(models.AbstractModel):
    _name = "report.caritas_fleet_request.report_personnel_trips_template"
    _description = "Personnel Trips Report"

    def _get_report_values(self, docids, data=None):
        data = data or {}
        if not data.get("driver_id"):
            raise ValidationError(_("Driver is required."))

        values = _prepare_trip_search_domain(data, self.env)
        trips = values.get("trips")

        return {
            "doc_ids": trips.ids,
            "doc_model": "vehicle.trip",
            "trips": trips,
            "vehicle": values.get("vehicle"),
            "department": values.get("department"),
            "driver": values.get("driver"),
            "date_from": values.get("date_from"),
            "date_to": values.get("date_to"),
            "total_trips": len(trips),
            "report_title": _("Personnel Trips Report"),
            "_": _,
        }