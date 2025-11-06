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
        comodel_name='hr.hospital.disease'
    )

    description = fields.Text()
    treatment = fields.Html()
    approved = fields.Boolean(default=False)

    doctor_id = fields.Many2one(
        comodel_name='hr.hospital.doctor',
        readonly=True
    )

    approved_date = fields.Datetime(readonly=True)

    severity = fields.Selection(
        selection=[
        ('light', 'Light'),
        ('medium', 'Medium'),
        ('hard', 'Hard'),
        ('critical', 'Critical'),
    ])
