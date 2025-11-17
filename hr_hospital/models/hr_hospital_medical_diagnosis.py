from datetime import datetime, timedelta
from odoo import fields, models, api, _


class HrHospitalMedicalDiagnosis(models.Model):
    _name = 'hr.hospital.medical.diagnosis'
    _description = 'Medical Diagnosis'

    name = fields.Char(required=True)

    # тільки завершені візити за останні 30 днів
    visit_id = fields.Many2one(
        comodel_name='hr.hospital.visit',
        string='Visit',
        ondelete='cascade',
        domain=lambda self: self._get_recent_completed_visits_domain()
    )

    # тільки заразні хвороби
    disease_id = fields.Many2one(
        comodel_name='hr.hospital.disease',
        domain=[
            ('is_contagious', '=', True),
            ('danger_level', 'in', ['high', 'critical']),
        ],
    )

    @api.model
    def _get_recent_completed_visits_domain(self):
        """Повертає домен для завершених візитів за останні 30 днів"""
        thirty_days_ago = datetime.now() - timedelta(days=30)
        return [
            ('status', '=', 'done'),
            ('planned_datetime', '>=', thirty_days_ago),
        ]

    description = fields.Text()
    treatment = fields.Html()
    approved = fields.Boolean(default=False)

    mentor_id = fields.Many2one(
        comodel_name='hr.hospital.doctor',
        readonly=True
    )

    @api.onchange('doctor_id')
    def _onchange_doctor_set_mentor(self):
        if self.doctor_id and self.doctor_id.is_intern:
            if self.doctor_id.mentor_id:
                self.mentor_id = self.doctor_id.mentor_id
                return {
                    'warning': {
                        'title': _("Intern Doctor"),
                        'message': _(
                            "Doctor is an intern. Mentor was assigned."
                        )
                    }
                }
        return {}

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
