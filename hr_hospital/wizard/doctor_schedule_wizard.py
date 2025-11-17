from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import timedelta


class DoctorScheduleWizard(models.TransientModel):
    _name = 'doctor.schedule.wizard'
    _description = 'Doctor Schedule Wizard'

    doctor_id = fields.Many2one(
        comodel_name='hr.hospital.doctor',
        string='Doctor',
        required=True,
    )

    week_start_date = fields.Date(
        string='Week Start Date',
        required=True,
        default=fields.Date.context_today,
    )

    weeks_count = fields.Integer(
        string='Number of Weeks',
        default=1,
        required=True,
    )

    schedule_type = fields.Selection(
        selection=[
            ('standard', 'Standard'),
            ('even_week', 'Even Week'),
            ('odd_week', 'Odd Week'),
        ],
        string='Schedule Type',
        default='standard',
        required=True,
    )

    # Days of week
    monday = fields.Boolean(string='Monday', default=True)
    tuesday = fields.Boolean(string='Tuesday', default=True)
    wednesday = fields.Boolean(string='Wednesday', default=True)
    thursday = fields.Boolean(string='Thursday', default=True)
    friday = fields.Boolean(string='Friday', default=True)
    saturday = fields.Boolean(string='Saturday', default=False)
    sunday = fields.Boolean(string='Sunday', default=False)

    # Time settings
    time_from = fields.Float(
        string='Start Time',
        default=9.0,
    )

    time_to = fields.Float(
        string='End Time',
        default=18.0,
    )

    break_from = fields.Float(
        string='Break Start',
        default=13.0,
    )

    break_to = fields.Float(
        string='Break End',
        default=14.0,
    )

    @api.constrains('weeks_count')
    def _check_weeks_count(self):
        """Ensure weeks count is positive"""
        for wizard in self:
            if wizard.weeks_count < 1:
                raise ValidationError(
                    _("Number of weeks must be at least 1!")
                )

    @api.constrains('time_from', 'time_to')
    def _check_time_valid(self):
        """Ensure times are valid"""
        for wizard in self:
            if wizard.time_from < 0 or wizard.time_from >= 24:
                raise ValidationError(_("Start time must be between 0:00 and 23:59!"))
            if wizard.time_to < 0 or wizard.time_to >= 24:
                raise ValidationError(_("End time must be between 0:00 and 23:59!"))
            if wizard.time_from >= wizard.time_to:
                raise ValidationError(_("Start time must be before end time!"))

            if wizard.break_from and wizard.break_to:
                if wizard.break_from < wizard.time_from or wizard.break_to > wizard.time_to:
                    raise ValidationError(_("Break time must be within working hours!"))
                if wizard.break_from >= wizard.break_to:
                    raise ValidationError(_("Break start must be before break end!"))

    def action_generate_schedule(self):
        """Generate doctor schedule"""
        self.ensure_one()

        # Check if at least one day is selected
        days_selected = any([
            self.monday, self.tuesday, self.wednesday, 
            self.thursday, self.friday, self.saturday, self.sunday
        ])

        if not days_selected:
            raise ValidationError(
                _("Please select at least one day of the week!")
            )

        # Map boolean fields to day names
        day_mapping = {
            0: ('monday', self.monday),
            1: ('tuesday', self.tuesday),
            2: ('wednesday', self.wednesday),
            3: ('thursday', self.thursday),
            4: ('friday', self.friday),
            5: ('saturday', self.saturday),
            6: ('sunday', self.sunday),
        }

        Schedule = self.env['hr.hospital.doctor.schedule']
        current_date = self.week_start_date
        created_count = 0

        # Generate schedule for each week
        for week_num in range(self.weeks_count):
            week_start = current_date + timedelta(days=week_num * 7)

            # Check if this week should be processed based on schedule type
            week_number = week_start.isocalendar()[1]

            if self.schedule_type == 'even_week' and week_number % 2 != 0:
                continue
            elif self.schedule_type == 'odd_week' and week_number % 2 == 0:
                continue

            # Generate schedule for each day of the week
            for day_offset in range(7):
                schedule_date = week_start + timedelta(days=day_offset)
                day_name, is_selected = day_mapping[day_offset]

                if not is_selected:
                    continue

                # Check if schedule already exists for this date
                existing = Schedule.search([
                    ('doctor_id', '=', self.doctor_id.id),
                    ('date', '=', schedule_date),
                ], limit=1)

                if existing:
                    # Update existing schedule
                    existing.write({
                        'time_from': self.time_from,
                        'time_to': self.time_to,
                        'type': 'work',
                    })
                else:
                    # Create morning shift (before break)
                    if self.break_from and self.break_to:
                        Schedule.create({
                            'doctor_id': self.doctor_id.id,
                            'date': schedule_date,
                            'day_of_week': day_name,
                            'time_from': self.time_from,
                            'time_to': self.break_from,
                            'type': 'work',
                        })

                        # Create afternoon shift (after break)
                        Schedule.create({
                            'doctor_id': self.doctor_id.id,
                            'date': schedule_date,
                            'day_of_week': day_name,
                            'time_from': self.break_to,
                            'time_to': self.time_to,
                            'type': 'work',
                        })
                        created_count += 2
                    else:
                        # Create full day schedule
                        Schedule.create({
                            'doctor_id': self.doctor_id.id,
                            'date': schedule_date,
                            'day_of_week': day_name,
                            'time_from': self.time_from,
                            'time_to': self.time_to,
                            'type': 'work',
                        })
                        created_count += 1

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Success'),
                'message': _('%s schedule entries have been created for %s') % (
                    created_count,
                    self.doctor_id.name
                ),
                'type': 'success',
                'sticky': False,
            }
        }
