from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class HrHospitalVisit(models.Model):
    _name = 'hr.hospital.visit'
    _description = 'Patient Visit'

    status = fields.Selection([
        ('planned', 'Planned'),
        ('in_progress', 'In Progress'),
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
    def unlink(self):
        for rec in self:
            if rec.diagnosis_ids:
                raise ValidationError(_("You cannot delete a visit that has diagnoses."))
        return super(Visit, self).unlink()

    recommendations = fields.Html()

    currency_id = fields.Many2one(
        comodel_name='res.currency',
        default=lambda self: self.env.company.currency_id
    )
    amount_total = fields.Monetary(
        currency_field='currency_id'
    )

    @api.constrains('planned_datetime', 'actual_datetime')
    def _check_test_date_after_assign(self):
        for rec in self:
            if rec.actual_datetime and rec.actual_datetime < rec.planned_datetime:
                raise ValidationError(_("Test date cannot be earlier than assignment date."))

    @api.constrains('patient_id', 'doctor_id', 'planned_datetime')
    def _check_unique_visit_same_day(self):
        for rec in self:
            if not rec.planned_datetime:
                continue
#TODO додати часовий пояс
            start_day = rec.planned_datetime.date()
            existing = self.search([
                ('id', '!=', rec.id),
                ('patient_id', '=', rec.patient_id.id),
                ('doctor_id', '=', rec.doctor_id.id),
                ('planned_datetime', '>=', start_day),
                ('planned_datetime', '<', start_day.replace(day=start_day.day+1))
            ], limit=1)

            if existing:
                raise ValidationError(_("Patient already has a visit to this doctor on that day."))

    def write(self, vals):
        for rec in self:
            if rec.status == 'done':
                blocked_fields = {'doctor_id', 'planned_datetime'}
                if blocked_fields.intersection(vals.keys()):
                    raise ValidationError(
                        _("You cannot change doctor, date or time of a completed visit.")
                    )
        return super(HrHospitalVisit, self).write(vals)