from odoo import models, fields


class HrHospitalDisease(models.Model):
    _name = 'hr.hospital.disease'
    _description = 'Disease'
    _parent_store = True
    _parent_name = 'parent_id'

    name = fields.Char(required=True)

    parent_id = fields.Many2one(
        'hr.hospital.disease',
        string="Parent Disease",
        ondelete='restrict'
    )
    child_ids = fields.One2many(
        'hr.hospital.disease',
        'parent_id',
        string="Child Diseases"
    )

    # ✅ обов’язкове поле для _parent_store
    parent_path = fields.Char(index=True)

    icd10_code = fields.Char(string="ICD-10 Code", size=10)

    danger_level = fields.Selection(
        [
            ('low', 'Low'),
            ('medium', 'Medium'),
            ('high', 'High'),
            ('critical', 'Critical')
        ],
        string="Danger Level",
        default='low'
    )

    contagious = fields.Boolean(string="Contagious")
    symptoms = fields.Text()

    spread_region_ids = fields.Many2many(
        'res.country',
        'disease_country_rel',
        'disease_id',
        'country_id',
        string="Spread Regions"
    )
    description = fields.Text()
