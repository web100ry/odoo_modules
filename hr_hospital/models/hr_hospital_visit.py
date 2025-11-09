from odoo import models, fields


class HrHospitalVisit(models.Model):
    _name = 'hr.hospital.visit'
    _description = 'Patient Visit'

    status = fields.Selection([
        ('planned', 'Planned'),
        ('done', 'Done'),
        ('cancelled', 'Cancelled'),
        ('no_show', 'No_show'),
    ], default='planned', required=True)

    planned_datetime = fields.Datetime(required=True)
    actual_datetime = fields.Datetime()

    doctor_id = fields.Many2one(
        comodel_name='hr.hospital.doctor',
        required=True
    )
    patient_id = fields.Many2one(
        comodel_name='hr.hospital.patient',
        required=True
    )

    visit_type = fields.Selection([
        ('primary', 'Primary'),
        ('secondary', 'Secondary'),
        ('preventive', 'Preventive'),
        ('urgent', 'Urgent'),
    ], required=True)

    diagnosis_ids = fields.One2many(
        comodel_name='hr.hospital.medical.diagnosis',
        inverse_name='visit_id',
        string='Diagnoses'
    )

    recommendations = fields.Html()

    currency_id = fields.Many2one(
        comodel_name='res.currency',
        default=lambda self: self.env.company.currency_id
    )
    amount_total = fields.Monetary(
        currency_field='currency_id'
    )
