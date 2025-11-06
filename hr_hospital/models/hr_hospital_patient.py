from odoo import models, fields


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
        'hr.hospital.doctor',
    )

    passport_data = fields.Char(
        size=10
    )

    contact_person_id = fields.Many2one(
        'hr.hospital.contact.person',
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
        'res.partner',
        domain=[('is_company', '=', True)]
    )

    insurance_policy_number = fields.Char()

    doctor_history_ids = fields.One2many(
        'hr.hospital.patient.doctor.history',
        'patient_id'
    )
