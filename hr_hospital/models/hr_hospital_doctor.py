from datetime import date
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

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
        #domain=[('is_intern', '=', False)]
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

    @api.constrains('mentor_id')
    def _check_mentor_is_not_intern(self):
        for rec in self:
            if rec.mentor_id and rec.mentor_id.is_intern:
                raise ValidationError(_("Intern cannot be chosen as a mentor."))

    @api.constrains('mentor_id')
    def _check_mentor_not_self(self):
        for rec in self:
            if rec.mentor_id and rec.mentor_id.id == rec.id:
                raise ValidationError(_("Doctor cannot be a mentor to themselves."))

    _sql_constraints = [
        ('unique_license', 'unique(license_number)', _('License number must be unique.')),
        ('check_rating', 'CHECK(rating >= 0 AND rating <= 5)', _('Rating must be between 0 and 5.'))
    ]
