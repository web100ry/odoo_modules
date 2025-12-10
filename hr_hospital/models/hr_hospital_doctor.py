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
        comodel_name='hr.hospital.doctor.speciality'
    )

    is_intern = fields.Boolean()

    # Складний домен: тільки лікарі, які НЕ є інтернами
    mentor_id = fields.Many2one(
        comodel_name='hr.hospital.doctor',
        domain="[('is_intern', '=', False), ('active', '=', True)]"
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

    education_country_id = fields.Many2one(comodel_name='res.country')

    active = fields.Boolean(default=True)

    visit_ids = fields.One2many('hr.hospital.visit', 'doctor_id')

    intern_ids = fields.One2many(
        comodel_name='hr.hospital.doctor',
        inverse_name='mentor_id',
        string='Interns'
    )

    intern_count = fields.Integer(
        compute='_compute_intern_count',
        string='Number of Interns'
    )

    @api.depends('intern_ids')
    def _compute_intern_count(self):
        for record in self:
            record.intern_count = len(record.intern_ids)

    def write(self, vals):
        if 'active' in vals and vals['active'] is False:
            for doctor in self:
                active_visits = self.env['hr.hospital.visit'].search([
                    ('doctor_id', '=', doctor.id),
                    ('status', 'in', ['planned', 'in_progress'])
                ], limit=1)

                if active_visits:
                    raise ValidationError(
                        _("You cannot archive a doctor with active visits.")
                    )
        return super(HrHospitalDoctor, self).write(vals)

    @api.depends('license_date')
    def _compute_experience(self):

        for record in self:
            if record.license_date:
                today = date.today()
                delta = today.year - record.license_date.year
                if ((today.month, today.day) <
                        (record.license_date.month,
                         record.license_date.day)):
                    delta -= 1
                record.experience_years = max(delta, 0)
            else:
                record.experience_years = 0

    @api.constrains('mentor_id')
    def _check_mentor_is_not_intern(self):
        for rec in self:
            if rec.mentor_id and rec.mentor_id.is_intern:
                raise ValidationError(
                    _("Intern cannot be chosen as a mentor.")
                )

    @api.constrains('mentor_id')
    def _check_mentor_not_self(self):
        for rec in self:
            if rec.mentor_id and rec.mentor_id.id == rec.id:
                raise ValidationError(
                    _("Doctor cannot be a mentor to themselves.")
                )

    _sql_constraints = [
        ('unique_license',
         'unique(license_number)',
         _('License number must be unique.')
         ),
        ('check_rating',
         'CHECK(rating >= 0 AND rating <= 5)',
         _('Rating must be between 0 and 5.')
         )
    ]

    # Динамічні методи для доменів
    @api.model
    def get_doctors_with_schedule(self):
        """Повертає домен для лікарів з заповненим розкладом"""
        doctors_with_schedule = (
            self.env[
                'hr.hospital.doctor.schedule'
            ].search([]).mapped('doctor_id')
        )
        return [('id', 'in', doctors_with_schedule.ids)]

    @api.model
    def get_doctors_by_speciality_and_schedule(
            self,
            speciality_id=None,
            schedule_date=None
    ):
        """
        Повертає домен для лікарів за спеціальністю та розкладом

        :param speciality_id: ID спеціальності
        :param schedule_date: Дата для перевірки розкладу
        :return: domain list
        """
        domain = [('active', '=', True)]

        if speciality_id:
            domain.append(('speciality_id', '=', speciality_id))

        if schedule_date:
            # Додаємо фільтр за розкладом на конкретну дату
            target_date = fields.Date.to_date(schedule_date)
            day_of_week = target_date.strftime('%A').lower()

            schedules = self.env['hr.hospital.doctor.schedule'].search([
                '|',
                ('date', '=', target_date),
                '&',
                ('date', '=', False),
                ('day_of_week', '=', day_of_week),
                ('type', '=', 'work'),
            ])

            if schedules:
                domain.append(('id', 'in', schedules.mapped('doctor_id').ids))

        return domain

    def action_view_interns(self):
        """Відкриває список інтернів поточного лікаря"""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Interns of %s', self.fullname),
            'res_model': 'hr.hospital.doctor',
            'view_mode': 'kanban,list,form',
            'domain': [('id', 'in', self.intern_ids.ids)],
            'context': {
                'default_mentor_id': self.id,
                'default_is_intern': True,
            }
        }

    def action_quick_create_visit(self):
        """Швидке створення візиту до лікаря з канбану"""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Новий візит до %s', self.fullname),
            'res_model': 'hr.hospital.visit',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_doctor_id': self.id,
                'default_status': 'planned',
            }
        }
