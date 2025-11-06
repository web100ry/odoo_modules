from odoo import models, fields


class HrHospitalDoctorSchedule(models.Model):
    _name = 'hr.hospital.doctor.schedule'
    _description = 'Doctor Schedule'

    doctor_id = fields.Many2one(
        'hr.hospital.doctor',
        required=True,
        ondelete='cascade'
    )
    day_of_week = fields.Selection(
        selection=[
            ('monday', 'MON'),
            ('tuesday', 'TUE'),
            ('wednesday', 'WED'),
            ('thursday', 'THU'),
            ('friday', 'FRI'),
            ('saturday', 'SAT'),
            ('sunday', 'SUN'),
        ])

    date = fields.Date()
    time_from = fields.Float()
    time_to = fields.Float()
    type = fields.Selection(
        selection=[
        ('work', 'Work Day'),
        ('vacation', 'Vacation'),
        ('sick', 'Sick'),
        ('conference', 'Conference'),
    ])
    note = fields.Char()
