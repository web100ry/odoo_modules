from datetime import date
from odoo import models, fields, api


class HrHospitalDoctor(models.Model):
    _name = 'hr.hospital.doctor'
    _description = 'Doctor'
    _inherit = ['hr.hospital.abstract.person']

    description = fields.Text()
    hospital_id = fields.Many2one(comodel_name='hr.hospital.hospital')

    user_id = fields.Many2one('res.users', string='Користувач системи')
    speciality_id = fields.Many2one('hr.hospital.doctor.speciality', string='Спеціальність')
    is_intern = fields.Boolean(string='Інтерн')
    mentor_id = fields.Many2one(
        'hr.hospital.doctor',
        string='Лікар-ментор',
        domain=[('is_intern', '=', False)]
    )

    license_number = fields.Char(
        string='Ліцензійний номер',
        required=True,
        copy=False
    )

    license_date = fields.Date(string='Дата видачі ліцензії')

    experience_years = fields.Integer(
        string='Досвід роботи (роки)',
        compute='_compute_experience',
        store=True
    )

    rating = fields.Float(
        string='Рейтинг',
        digits=(3, 2),
        default=0.00
    )

    schedule_ids = fields.One2many(
        'hr.hospital.doctor.schedule',
        'doctor_id',
        string='Графік роботи'
    )

    education_country_id = fields.Many2one(
        'res.country',
        string='Країна навчання'
    )

    @api.depends('license_date')
    def _compute_experience(self):
        """кількість років досвіду від дати видачі ліцензії"""
        for record in self:
            if record.license_date:
                today = date.today()
                delta = today.year - record.license_date.year
                if (today.month, today.day) < (record.license_date.month, record.license_date.day):
                    delta -= 1
                record.experience_years = max(delta, 0)
            else:
                record.experience_years = 0
