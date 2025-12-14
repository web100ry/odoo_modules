from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class HrHospitalPatient(models.Model):
    _name = 'hr.hospital.patient'
    _description = 'Patient'
    _inherit = ['hr.hospital.abstract.person']

    # Динамічні методи для доменів
    @api.model
    def get_patients_by_language_and_country(
            self,
            lang_id=None,
            country_id=None
    ):

        domain = []

        if lang_id:
            domain.append(('lang_id', '=', lang_id))

        if country_id:
            domain.append(('country_id', '=', country_id))

        return domain

    @api.model
    def search_patients_by_language(self, language_code):

        lang = self.env['res.lang'].search(
            [('code', '=', language_code)],
            limit=1
        )
        if lang:
            return self.search([('lang_id', '=', lang.id)])
        return self.env['hr.hospital.patient']

    @api.model
    def search_patients_by_country(self, country_code):

        country = self.env['res.country'].search(
            [('code', '=', country_code)],
            limit=1
        )
        if country:
            return self.search(
                [('country_id', '=', country.id)]
            )
        return self.env['hr.hospital.patient']

    disease_id = fields.Many2one(
        comodel_name='hr.hospital.disease',
    )
    doctor_id = fields.Many2one(
        comodel_name='hr.hospital.doctor',
    )

    personal_doctor_id = fields.Many2one(
        comodel_name='hr.hospital.doctor',
    )

    @api.model
    def create(self, vals):
        patient = super().create(vals)

        if vals.get('personal_doctor_id'):
            self.env['hr.hospital.patient.doctor.history'].create({
                'patient_id': patient.id,
                'doctor_id': vals['personal_doctor_id'],
                'change_date': fields.Datetime.now(),
                'reason_change': _('Initial doctor assignment')
            })
        return patient

    def write(self, vals):
        for patient in self:
            if (
                    'personal_doctor_id' in vals
                    and vals['personal_doctor_id']
                    != patient.personal_doctor_id.id
            ):
                self.env[
                    'hr.hospital.patient.doctor.history'
                ].create({
                    'patient_id': patient.id,
                    'doctor_id': vals['personal_doctor_id'],
                    'change_date': fields.Datetime.now(),
                    'reason_change': _(
                        'Doctor changed automatically'
                    ),
                })

        return super().write(vals)

    passport_data = fields.Char(
        size=10
    )

    contact_person_id = fields.Many2one(
        comodel_name='hr.hospital.contact.person',
    )

    blood_type = fields.Selection(
        selection=[
            ('o_plus', 'O(I) Rh+'),
            ('o_minus', 'O(I) Rh−'),
            ('a_plus', 'A(II) Rh+'),
            ('a_minus', 'A(II) Rh−'),
            ('b_plus', 'B(III) Rh+'),
            ('b_minus', 'B(III) Rh−'),
            ('ab_plus', 'AB(IV) Rh+'),
            ('ab_minus', 'AB(IV) Rh−'),
        ])

    allergies = fields.Text()

    insurance_company_id = fields.Many2one(
        comodel_name='res.partner',
        domain=[('is_company', '=', True)]
    )

    insurance_policy_number = fields.Char()

    doctor_history_ids = fields.One2many(
        comodel_name='hr.hospital.patient.doctor.history',
        inverse_name='patient_id'
    )

    visit_ids = fields.One2many(
        comodel_name='hr.hospital.visit',
        inverse_name='patient_id',
        string='Visits'
    )

    visit_count = fields.Integer(
        compute='_compute_visit_count'
    )

    @api.depends('visit_ids')
    def _compute_visit_count(self):
        for patient in self:
            patient.visit_count = len(patient.visit_ids)

    visit_ids = fields.One2many(
        comodel_name='hr.hospital.visit',
        inverse_name='patient_id',
        string='Visits'
    )

    @api.depends('visit_ids')
    def _compute_visit_count(self):
        for patient in self:
            patient.visit_count = len(patient.visit_ids)

    def action_view_visits(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Patient Visits'),
            'res_model': 'hr.hospital.visit',
            'view_mode': 'list,form,calendar',
            'domain': [('patient_id', '=', self.id)],
            'context': {'default_patient_id': self.id}
        }

    @api.constrains('birth_date')
    def _check_age_positive(self):
        from datetime import date
        for rec in self:
            if rec.birth_date:
                if rec.birth_date >= date.today():
                    raise ValidationError(_("Birth date must be in the past."))

    @api.constrains('age')
    def _check_age_positive(self):
        for rec in self:
            if rec.age < 0:
                raise ValidationError(
                    _("Age must be greater than 0.")
                )

    @api.onchange('country_id')
    def _onchange_country_suggest_language(self):
        # Якщо країни немає — очистити мову й повернути пустий warning
        if not self.country_id:
            self.lang_id = False
            return {'warning': {}}

        mapping = {
            'UA': 'uk_UA',
            'PL': 'pl_PL',
            'DE': 'de_DE',
            'US': 'en_US',
            'GB': 'en_GB',
        }

        lang_code = mapping.get(self.country_id.code)
        if not lang_code:
            self.lang_id = False
            return {'warning': {}}

        lang = self.env['res.lang'].search(
            [('code', '=', lang_code)],
            limit=1
        )
        if not lang:
            self.lang_id = False
            return {'warning': {}}

        self.lang_id = lang

        return {
            'warning': {
                'title': _("Language Suggestion"),
                'message': _(
                    "Based on the selected citizenship (%(country)s), the recommended communication language is: %(lang)s"
                ) % {
                     'country': self.country_id.name,
                      'lang': lang.name
                    }
            }
        }
