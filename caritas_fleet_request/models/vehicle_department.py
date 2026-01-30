from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class VehicleDepartment(models.Model):
    _name = "vehicle.department"
    _description = "Vehicle Department"
    _order = "name"

    name = fields.Char(
        string="Department Name",
        required=True,
    )

    user_ids = fields.Many2many(
        comodel_name="res.users",
        relation="vehicle_department_user_rel",
        column1="department_id",
        column2="user_id",
        string="Employees",
    )

    driver_ids = fields.Many2many(
        comodel_name="res.users",
        relation="vehicle_department_driver_rel",
        column1="department_id",
        column2="driver_id",
        string="Drivers",
    )

    vehicle_ids = fields.One2many(
        comodel_name="fleet.vehicle",
        inverse_name="department_id",
        string="Vehicles",
    )

    vehicle_selection_ids = fields.Many2many(
        comodel_name="fleet.vehicle",
        compute="_compute_vehicle_selection_ids",
        inverse="_inverse_vehicle_selection_ids",
        string="Vehicles",
    )

    active = fields.Boolean(
        default=True
    )

    @api.depends("vehicle_ids")
    def _compute_vehicle_selection_ids(self):
        for department in self:
            department.vehicle_selection_ids = department.vehicle_ids

    def _inverse_vehicle_selection_ids(self):
        for department in self:
            vehicles_to_assign = department.vehicle_selection_ids
            removed_vehicles = department.vehicle_ids - vehicles_to_assign

            for vehicle in vehicles_to_assign:
                vehicle.department_id = department.id

            for vehicle in removed_vehicles:
                if vehicle.department_id == department:
                    vehicle.department_id = False

    @api.constrains("driver_ids")
    def _check_driver_ids(self):
        driver_group = self.env.ref("caritas_fleet_request.group_fleet_driver", raise_if_not_found=False)
        for department in self:
            if driver_group:
                invalid_group = department.driver_ids.filtered(lambda u: driver_group not in u.groups_id)
                if invalid_group:
                    raise ValidationError(_("Drivers must belong to the Fleet Driver group."))
            if department.user_ids:
                outside_employees = department.driver_ids - department.user_ids
                if outside_employees:
                    raise ValidationError(_("Drivers must be selected among department employees."))