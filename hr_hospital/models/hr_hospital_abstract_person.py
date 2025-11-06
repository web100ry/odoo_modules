import re
from datetime import date
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


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
        selection=[
            ('male', 'Male'),
            ('female', 'Female'),
            ('other', 'Other')
        ])

    birth_date = fields.Date()
    age = fields.Integer(
        compute="_compute_age",
        store=True,
        readonly=False
    )

    fullname = fields.Char(
        compute="_compute_fullname",
        store=True,
        readonly=False
    )

    country_id = fields.Many2one('res.country')
    lang_id = fields.Many2one('res.lang')

    @api.constrains('phone')
    def _check_phone_format(self):
        for record in self:
            if record.phone and not re.match(r'^\+380\d{9}$', record.phone):
                raise ValidationError(
                    _("The phone number must be in the format +380XXXXXXXXX")
                )

    @api.constrains('email')
    def _check_email_format(self):
        for record in self:
            if record.email and not re.match(
                    r"[^@]+@[^@]+\.[^@]+",
                    record.email
            ):
                raise ValidationError(_("Invalid email format"))

    @api.depends('birth_date')
    def _compute_age(self):
        today = date.today()
        for record in self:
            if record.birth_date:
                years = today.year - record.birth_date.year
                # Якщо день народження ще не настав у цьому році — відняти 1
                if ((today.month, today.day) <
                        (record.birth_date.month, record.birth_date.day)):
                    years -= 1
                record.age = years
            else:
                record.age = 0

    @api.depends('first_name', 'middle_name', 'last_name')
    def _compute_fullname(self):
        for record in self:
            parts = [
                record.first_name or '',
                record.last_name or '',
                record.middle_name or ''
            ]
            record.fullname = ' '.join(p for p in parts if p).strip()
