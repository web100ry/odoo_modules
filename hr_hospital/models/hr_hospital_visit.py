from odoo import models, fields


class HrHospitalVisit(models.Model):
    _name = 'hr.hospital.visit'
    _description = 'Patient Visit'

    status = fields.Selection([
        ('planned', 'Заплановано'),
        ('done', 'Завершено'),
        ('cancelled', 'Скасовано'),
        ('no_show', 'Не зʼявився'),
    ], default='planned', required=True)

    planned_datetime = fields.Datetime(required=True)
    actual_datetime = fields.Datetime()

    doctor_id = fields.Many2one('hr.hospital.doctor', required=True)
    patient_id = fields.Many2one('hr.hospital.patient', required=True)

    visit_type = fields.Selection([
        ('primary', 'Первинний'),
        ('secondary', 'Повторний'),
        ('preventive', 'Профілактичний'),
        ('urgent', 'Невідкладний'),
    ], required=True)

    diagnosis_ids = fields.One2many(
        'hr.hospital.medical.diagnosis',
        'visit_id',
        string='Diagnoses'
    )

    recommendations = fields.Html()

    currency_id = fields.Many2one('res.currency', default=lambda self: self.env.company.currency_id)
    amount_total = fields.Monetary(currency_field='currency_id')
