from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class HrHospitalPatient(models.Model):
    _name = 'hr.hospital.patient'
    _description = 'Patient'
    _inherit = ['hr.hospital.abstract.person']

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
            if ('personal_doctor_id' in vals and
                    vals['personal_doctor_id'] != patient.personal_doctor_id.id):

                self.env['hr.hospital.patient.doctor.history'].create({
                    'patient_id': patient.id,
                    'doctor_id': vals['personal_doctor_id'],
                    'change_date': fields.Datetime.now(),
                    'reason_change': _('Doctor changed automatically')
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
                raise ValidationError(_("Age must be greater than 0."))

