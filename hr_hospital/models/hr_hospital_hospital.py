import logging

from odoo import models, fields
_logger = logging.getLogger(__name__)


class HrHospital(models.Model):
    _name = 'hr.hospital.hospital'
    _description = 'Hospital'

    name = fields.Char()
    branchid = fields.Char()
    description = fields.Text()

    res_partner_id = fields.Many2one(
        comodel_name='res.partner',
        string="Director",
    )
    res_partner_ids = fields.Many2many(
        comodel_name='res.partner',
        string="Doctor",
    )
