from datetime import date
from odoo import models, fields, api


class HrHospitalDoctor(models.Model):
    _name = 'hr.hospital.doctor'
    _description = 'Doctor'
    _inherit = ['hr.hospital.abstract.person']

    description = fields.Text()
    hospital_id = fields.Many2one(
        comodel_name='hr.hospital.hospital'
    )

    user_id = fields.Many2one(
        comodel_name='res.users'
    )
    speciality_id = fields.Many2one(
        comodel_name= 'hr.hospital.doctor.speciality'
    )
    is_intern = fields.Boolean()
    mentor_id = fields.Many2one(
        comodel_name='hr.hospital.doctor',
        domain=[('is_intern', '=', False)]
    )

    license_number = fields.Char(
        required=True,
        copy=False
    )

    license_date = fields.Date()

    experience_years = fields.Integer(
        compute='_compute_experience',
        store=True
    )

    rating = fields.Float(
        digits=(3, 2),
        default=0.00
    )

    schedule_ids = fields.One2many(
        comodel_name='hr.hospital.doctor.schedule',
        inverse_name='doctor_id',
    )

    education_country_id = fields.Many2one(
        comodel_name='res.country'
    )

    @api.depends('license_date')
    def _compute_experience(self):

        for record in self:
            if record.license_date:
                today = date.today()
                delta = today.year - record.license_date.year
                if ((today.month, today.day) <
                        (record.license_date.month, record.license_date.day)):
                    delta -= 1
                record.experience_years = max(delta, 0)
            else:
                record.experience_years = 0
