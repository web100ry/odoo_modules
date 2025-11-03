from odoo import models, fields

class HrHospitalDoctorSpeciality(models.Model):
    _name = 'hr.hospital.doctor.speciality'
    _description = 'Doctor Speciality'

    name = fields.Char(required=True)
    code = fields.Char(string="Код спеціальності", required=True, size=10)
    description = fields.Text(string="Опис")
    active = fields.Boolean(default=True)
    doctor_ids = fields.One2many('hr.hospital.doctor', 'speciality_id')
