from odoo import fields, models


class HrHospitalMedicalDiagnosis(models.Model):
    _name = 'hr.hospital.medical.diagnosis'
    _description = 'Medical Diagnosis'

    visit_id = fields.Many2one(
        'hr.hospital.visit',
        string='Visit',
        ondelete='cascade'
    )


    disease_id = fields.Many2one(
        comodel_name='hr.hospital.disease',
        string='Хвороба'
    )

    description = fields.Text(string="Опис діагнозу")
    treatment = fields.Html(string="Лікування")
    approved = fields.Boolean(default=False, string="Затверджено")

    doctor_id = fields.Many2one(
        comodel_name='hr.hospital.doctor',
        string="Лікар, що затвердив",
        readonly=True
    )

    approved_date = fields.Datetime(readonly=True)

    severity = fields.Selection([
        ('light', 'Легкий'),
        ('medium', 'Середній'),
        ('hard', 'Тяжкий'),
        ('critical', 'Критичний'),
    ], string="Ступінь тяжкості")
