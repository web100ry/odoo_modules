from datetime import timedelta
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class HrHospitalVisit(models.Model):
    _name = 'hr.hospital.visit'
    _description = 'Patient Visit'

    status = fields.Selection(
        selection=[
            ('planned', 'Planned'),
            ('in_progress', 'In Progress'),
            ('done', 'Done'),
            ('cancelled', 'Cancelled'),
            ('no_show', 'No_show'),
        ],
        default='planned',
        required=True
    )

    planned_datetime = fields.Datetime(required=True)
    actual_datetime = fields.Datetime()

    # Складний домен: тільки лікарі з заповненим ліцензійним номером
    doctor_id = fields.Many2one(
        comodel_name='hr.hospital.doctor',
        required=True,
        domain=[
            ('license_number', '!=', False),
            ('license_number', '!=', '')
        ]
    )
    patient_id = fields.Many2one(
        comodel_name='hr.hospital.patient',
        required=True
    )

    visit_type = fields.Selection(
        selection=[
            ('primary', 'Primary'),
            ('secondary', 'Secondary'),
            ('preventive', 'Preventive'),
            ('urgent', 'Urgent'),
        ],
        required=True
    )

    diagnosis_ids = fields.One2many(
        comodel_name='hr.hospital.medical.diagnosis',
        inverse_name='visit_id',
    )

    diagnosis_count = fields.Integer(
        compute="_compute_diagnosis_count",
        store=True,
        readonly=True,
    )

    @api.depends('diagnosis_ids')
    def _compute_diagnosis_count(self):
        for rec in self:
            rec.diagnosis_count = len(rec.diagnosis_ids)

    def unlink(self):
        for rec in self:
            if rec.diagnosis_ids:
                raise ValidationError(_("You cannot delete a "
                                        "visit that has diagnoses."))
        return super(HrHospitalVisit, self).unlink()

    recommendations = fields.Html()

    currency_id = fields.Many2one(
        comodel_name='res.currency',
        default=lambda self: self.env.company.currency_id
    )
    amount_total = fields.Monetary(
        currency_field='currency_id'
    )

    @api.constrains('planned_datetime', 'actual_datetime')
    def _check_test_date_after_assign(self):
        for rec in self:
            if (rec.actual_datetime and rec.actual_datetime
                    < rec.planned_datetime):
                raise ValidationError(_("Test date cannot be earlier"
                                        " than assignment date."))

    @api.constrains('patient_id', 'doctor_id', 'planned_datetime')
    def _check_unique_visit_same_day(self):
        for rec in self:
            if not rec.planned_datetime:
                continue

            start_day = rec.planned_datetime.date()
            next_day = start_day + timedelta(days=1)

            existing = self.search([
                ('id', '!=', rec.id),
                ('patient_id', '=', rec.patient_id.id),
                ('doctor_id', '=', rec.doctor_id.id),
                ('planned_datetime', '>=', start_day),
                ('planned_datetime', '<', next_day)
            ], limit=1)

            if existing:
                raise ValidationError(
                    _("Patient already has a "
                      "visit to this doctor on that day.")
                )

    def write(self, vals):
        for rec in self:
            if rec.status == 'done':
                blocked_fields = {'doctor_id', 'planned_datetime'}
                if blocked_fields.intersection(vals.keys()):
                    raise ValidationError(
                        _("You cannot change doctor, "
                          "date or time of a completed visit.")
                    )
        return super(HrHospitalVisit, self).write(vals)

    @api.onchange('patient_id')
    def _onchange_patient_warning_allergies(self):
        if self.patient_id and self.patient_id.allergies:
            return {
                'warning': {
                    'title': _("Allergy Warning"),
                    'message': _(
                        "This patient has allergies: %s"
                    ) % self.patient_id.allergies
                }
            }
        return {}

    @api.model
    def get_available_doctors_domain(self, speciality_id=None, date=None):

        domain = [
            ('active', '=', True),
            ('license_number', '!=', False),
            ('license_number', '!=', ''),
        ]

        if speciality_id:
            domain.append(('speciality_id', '=', speciality_id))

        if date:
            # Знаходимо лікарів, які мають розклад на цю дату
            target_date = fields.Date.to_date(date)
            day_of_week = target_date.strftime('%A').lower()

            schedules = self.env['hr.hospital.doctor.schedule'].search([
                '|',
                ('date', '=', target_date),
                '&',
                ('date', '=', False),
                ('day_of_week', '=', day_of_week),
                ('type', '=', 'work'),
            ])

            available_doctor_ids = schedules.mapped('doctor_id').ids
            if available_doctor_ids:
                domain.append(('id', 'in', available_doctor_ids))

        return domain

    @api.model
    def get_possible_visit_dates(self, doctor_id, days_ahead=30):

        if not doctor_id:
            return []

        doctor = self.env['hr.hospital.doctor'].browse(doctor_id)
        if not doctor.exists():
            return []

        possible_dates = []
        today = fields.Date.today()

        for i in range(days_ahead):
            check_date = today + timedelta(days=i)
            day_of_week = check_date.strftime('%A').lower()

            # Перевіряємо чи є робочий розклад на цю дату
            work_schedule = self.env['hr.hospital.doctor.schedule'].search([
                ('doctor_id', '=', doctor_id),
                '|',
                ('date', '=', check_date),
                '&',
                ('date', '=', False),
                ('day_of_week', '=', day_of_week),
                ('type', '=', 'work'),
            ], limit=1)

            # Перевіряємо чи немає відпустки/лікарняного
            vacation_schedule = self.env[
                'hr.hospital.doctor.schedule'
            ].search([
                ('doctor_id', '=', doctor_id),
                ('date', '=', check_date),
                ('type', 'in', ['vacation', 'sick']),
            ], limit=1)

            if work_schedule and not vacation_schedule:
                possible_dates.append(check_date)

        return possible_dates

    @api.model
    def get_doctors_by_education_country(self, country_id):
        """
        Повертає домен для лікарів за країною навчання

        :param country_id: ID країни
        :return: domain list
        """
        return [
            ('education_country_id', '=', country_id),
            ('active', '=', True),
        ]
