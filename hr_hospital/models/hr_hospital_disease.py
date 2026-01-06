from odoo import models, fields


class HrHospitalDisease(models.Model):
    """
    Represents a disease or medical condition.
    Can be organized in a hierarchy (ICD-10).
    """
    _name = 'hr.hospital.disease'
    _description = 'Hospital Diseases'

    name = fields.Char(required=True, translate=True)
    icd10_code = fields.Char(size=10)

    parent_id = fields.Many2one(
        comodel_name='hr.hospital.disease',
    )
    child_ids = fields.One2many(
        comodel_name='hr.hospital.disease',
        inverse_name='parent_id'
    )

    danger_level = fields.Selection(
        selection=[
            ('low', 'Low'),
            ('medium', 'Medium'),
            ('high', 'High'),
            ('critical', 'Critical'),
        ])

    is_contagious = fields.Boolean()
    symptoms = fields.Text(translate=True)
    region_ids = fields.Many2many('res.country')
    description = fields.Text(translate=True)
