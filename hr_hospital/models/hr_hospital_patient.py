from odoo import models, fields


class HrHospitalPatient(models.Model):
    _name = 'hr.hospital.patient'
    _description = 'Patient'
    _inherit = ['hr.hospital.abstract.person']

    disease_id = fields.Many2one(
        comodel_name='hr.hospital.disease',
        string='Діагноз'
    )
    doctor_id = fields.Many2one(
        comodel_name='hr.hospital.doctor',
        string='Поточний лікар'
    )

    personal_doctor_id = fields.Many2one(
        'hr.hospital.doctor',
        string='Персональний лікар'
    )

    passport_data = fields.Char(
        string='Паспортні дані',
        size=10
    )

    contact_person_id = fields.Many2one(
        'hr.hospital.contact.person',
        string='Контактна особа'
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
        ],
        string='Група крові'
    )

    allergies = fields.Text(string='Алергії')

    insurance_company_id = fields.Many2one(
        'res.partner',
        string='Страхова компанія',
        domain=[('is_company', '=', True)]
    )

    insurance_policy_number = fields.Char(string='Номер страхового поліса')

