from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class FleetVehicle(models.Model):
    _inherit = "fleet.vehicle"

    department_id = fields.Many2one(
        comodel_name="vehicle.department",
        string="Department",
    )

    responsible_driver_id = fields.Many2one(
        comodel_name="res.users",
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
        string="Responsible Driver",
    )

    availability_status = fields.Selection(
        selection=[
            ("available", "Available"),
            ("reserved", "Reserved"),
            ("unavailable", "Unavailable"),
        ],
        default="available",
        string="Availability Status",
    )

    @api.constrains("responsible_driver_id")
    def _check_responsible_driver_group(self):
        driver_group = self.env.ref("caritas_fleet_request.group_fleet_driver", raise_if_not_found=False)
        for vehicle in self:
            if vehicle.responsible_driver_id and driver_group and driver_group not in vehicle.responsible_driver_id.groups_id:
                raise ValidationError(
                    _("Responsible Driver must belong to the Fleet Driver group."),
                )