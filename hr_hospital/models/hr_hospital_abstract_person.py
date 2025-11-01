from odoo import models, fields, api
from datetime import date
import re

class AbstractPerson(models.AbstractModel):
    _name = 'hr.hospital.abstract.person'
    _description = 'Abstract Person'
    _inherit = ['image.mixin']

    last_name = fields.Char(required=True)
    first_name = fields.Char(required=True)
    middle_name = fields.Char()

    phone = fields.Char()
    email = fields.Char()
    gender = fields.Selection(
        selection=[('male', 'Male'), ('female', 'Female'),('other', 'Other')])

    birth_date = fields.Date(string="Дата народження")
    age = fields.Integer(string="Вік", compute="_compute_age", store=True, readonly=False)
    fullname = fields.Char(compute="_compute_fullname", store=True, readonly=False)

    @api.depends('birth_date')
    def _compute_age(self):
        today = date.today()
        for record in self:
            if record.birth_date:
                # Обчислення різниці років
                years = today.year - record.birth_date.year
                # Якщо день народження ще не настав у цьому році — відняти 1
                if (today.month, today.day) < (record.birth_date.month, record.birth_date.day):
                    years -= 1
                record.age = years
            else:
                record.age = 0

    @api.depends('first_name', 'middle_name', 'last_name')
    def _compute_fullname(self):
        for record in self:
            parts = [record.last_name or '', record.first_name or '', record.middle_name or '']
            record.fullname = ' '.join(p for p in parts if p).strip()

