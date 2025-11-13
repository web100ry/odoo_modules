from odoo import fields, models


class HrHospitalMedicalDiagnosis(models.Model):
    _name = 'hr.hospital.medical.diagnosis'
    _description = 'Medical Diagnosis'

    name= fields.Char(required=True)

    visit_id = fields.Many2one(
        comodel_name='hr.hospital.visit',
        string='Visit',
        ondelete='cascade'
    )

    disease_id = fields.Many2one(
        comodel_name='hr.hospital.disease'
    )

    description = fields.Text()
    treatment = fields.Html()
    approved = fields.Boolean(default=False)

    mentor_id = fields.Many2one(
        comodel_name='hr.hospital.doctor',
        readonly=True
    )

    approved_date = fields.Datetime()

    severity = fields.Selection(
        selection=[
            ('light', 'Light'),
            ('medium', 'Medium'),
            ('hard', 'Hard'),
            ('critical', 'Critical'),
        ])
    def action_approve_by_mentor(self):
        for record in self:
            record.write({
                'approved': True,
                'approved_date': fields.Datetime.now()
            })