from odoo import models, fields


class HrHospitalContactPerson(models.Model):
    _name = 'hr.hospital.contact.person'
    _description = 'Contact Person'
    _inherit = ['hr.hospital.abstract.person']

    # Складний домен: тільки пацієнти з заповненими алергіями
    patient_id = fields.Many2one(
        comodel_name='hr.hospital.patient',
        domain="[('allergies', '!=', False), ('allergies', '!=', '')]"
    )
