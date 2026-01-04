from datetime import datetime, timedelta
from odoo import fields, models, api


class HrHospitalMedicalDiagnosis(models.Model):
    """
    Stores medical diagnoses for patients during their visits.
    Includes details about the disease, treatment, and approval by mentor.
    """
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

    # логічний прапорець «погоджено»
    approved = fields.Boolean(default=False)

    mentor_id = fields.Many2one(
        comodel_name='hr.hospital.doctor',
        readonly=True
    )

    # основна дата діагнозу — Datetime
    diagnosis_date = fields.Datetime(
        default=fields.Datetime.now,
        required=True
    )

    diagnosis_year = fields.Integer(
        compute='_compute_diagnosis_period',
        store=True
    )

    diagnosis_month = fields.Integer(
        compute='_compute_diagnosis_period',
        store=True
    )

    disease_type = fields.Char(
        related='disease_id.parent_id.name',
        store=True
    )

    approved_date = fields.Datetime()

    severity = fields.Selection(
        selection=[
            ('light', 'Light'),
            ('medium', 'Medium'),
            ('hard', 'Hard'),
            ('critical', 'Critical'),
        ]
    )

    # кількість діагнозів (для pivot/graph)
    diagnosis_count = fields.Integer(
        default=1,
        readonly=True,
        group_operator="sum",
    )

    status = fields.Selection(
        selection=[
            ('draft', 'Draft'),
            ('approved', 'Approved'),
        ],
        string="Статус",
        default='draft'
    )

    def action_approve_by_mentor(self):
        """Кнопка затвердження діагнозу ментором"""
        for record in self:
            record.write({
                'approved': True,
                'approved_date': fields.Datetime.now(),
                'status': 'approved',
            })

    @api.depends('diagnosis_date')
    def _compute_diagnosis_period(self):
        for rec in self:
            if rec.diagnosis_date:
                # diagnosis_date — Datetime
                rec.diagnosis_year = rec.diagnosis_date.year
                rec.diagnosis_month = rec.diagnosis_date.month
            else:
                rec.diagnosis_year = False
                rec.diagnosis_month = False
