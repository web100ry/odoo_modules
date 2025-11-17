from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class RescheduleVisitWizard(models.TransientModel):
    _name = 'reschedule.visit.wizard'
    _description = 'Reschedule Visit Wizard'

    visit_id = fields.Many2one(
        comodel_name='hr.hospital.visit',
        string='Current Visit',
        readonly=True,
        required=True,
    )

    current_doctor_id = fields.Many2one(
        comodel_name='hr.hospital.doctor',
        string='Current Doctor',
        related='visit_id.doctor_id',
        readonly=True,
    )

    current_datetime = fields.Datetime(
        string='Current Date & Time',
        related='visit_id.planned_datetime',
        readonly=True,
    )

    new_doctor_id = fields.Many2one(
        comodel_name='hr.hospital.doctor',
        string='New Doctor',
    )

    new_date = fields.Date(
        string='New Date',
        required=True,
        default=fields.Date.context_today,
    )

    new_time = fields.Float(
        string='New Time',
        required=True,
        default=9.0,
    )

    reschedule_reason = fields.Text(
        string='Reason for Rescheduling',
        required=True,
    )

    @api.model
    def default_get(self, fields_list):
        """Set default values from context"""
        res = super().default_get(fields_list)

        # Get visit_id from context (when called from visit form)
        if self.env.context.get('active_model') == 'hr.hospital.visit':
            visit_id = self.env.context.get('active_id')
            if visit_id:
                res['visit_id'] = visit_id

        return res

    @api.constrains('new_time')
    def _check_time_valid(self):
        """Ensure time is valid (0-24)"""
        for wizard in self:
            if wizard.new_time < 0 or wizard.new_time >= 24:
                raise ValidationError(
                    _("Time must be between 0:00 and 23:59!")
                )

    @api.constrains('new_date')
    def _check_date_future(self):
        """Ensure new date is not in the past"""
        for wizard in self:
            if wizard.new_date < fields.Date.today():
                raise ValidationError(
                    _("New date cannot be in the past!")
                )

    def action_reschedule(self):
        """Reschedule the visit"""
        self.ensure_one()

        if not self.visit_id:
            raise ValidationError(_("No visit selected!"))

        # Check if visit can be rescheduled
        if self.visit_id.status not in ['planned']:
            raise ValidationError(
                _("Only planned visits can be rescheduled!")
            )

        # Combine date and time
        new_datetime = fields.Datetime.to_datetime(self.new_date)
        hours = int(self.new_time)
        minutes = int((self.new_time - hours) * 60)
        new_datetime = new_datetime.replace(hour=hours, minute=minutes)

        # Determine the doctor (new or current)
        doctor_id = self.new_doctor_id.id if self.new_doctor_id else self.visit_id.doctor_id.id

        # Check for conflicts
        conflicting_visit = self.env['hr.hospital.visit'].search([
            ('id', '!=', self.visit_id.id),
            ('doctor_id', '=', doctor_id),
            ('patient_id', '=', self.visit_id.patient_id.id),
            ('planned_datetime', '=', new_datetime),
            ('status', 'in', ['planned', 'in_progress']),
        ], limit=1)

        if conflicting_visit:
            raise ValidationError(
                _("There is already a visit scheduled for this patient with this doctor at this time!")
            )

        # Update the visit
        update_vals = {
            'planned_datetime': new_datetime,
        }

        if self.new_doctor_id:
            update_vals['doctor_id'] = self.new_doctor_id.id

        self.visit_id.write(update_vals)

        # Log the rescheduling in chatter
        self.visit_id.message_post(
            body=_("Visit rescheduled. Reason: %s") % self.reschedule_reason,
            subject=_("Visit Rescheduled"),
        )

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Success'),
                'message': _('Visit has been rescheduled successfully!'),
                'type': 'success',
                'sticky': False,
            }
        }
