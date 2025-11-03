from odoo import models, fields


class HrHospitalDoctorSchedule(models.Model):
    _name = 'hr.hospital.doctor.schedule'
    _description = 'Doctor Schedule'

    doctor_id = fields.Many2one('hr.hospital.doctor', string="Лікар", required=True, ondelete='cascade')
    day_of_week = fields.Selection([
        ('monday', 'Понеділок'),
        ('tuesday', 'Вівторок'),
        ('wednesday', 'Середа'),
        ('thursday', 'Четвер'),
        ('friday', 'П’ятниця'),
        ('saturday', 'Субота'),
        ('sunday', 'Неділя'),
    ], string="День тижня")

    date = fields.Date(string="Дата")
    time_from = fields.Float(string="Час початку")
    time_to = fields.Float(string="Час завершення")
    type = fields.Selection([
        ('work', 'Робочий день'),
        ('vacation', 'Відпустка'),
        ('sick', 'Лікарняний'),
        ('conference', 'Конференція'),
    ], string="Тип")
    note = fields.Char(string="Примітки")
