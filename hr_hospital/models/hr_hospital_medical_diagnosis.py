from odoo import fields, models, api, _


class HrHospitalMedicalDiagnosis(models.Model):
    _name = 'hr.hospital.medical.diagnosis'
    _description = 'Medical Diagnosis'

    name= fields.Char(required=True)

    visit_id = fields.Many2one(
        comodel_name='hr.hospital.visit',
        string='Visit',
        ondelete='cascade'
    )

    disease_id = fields.Many2one(
        comodel_name='hr.hospital.disease'
    )

    description = fields.Text()
    treatment = fields.Html()
    approved = fields.Boolean(default=False)

    mentor_id = fields.Many2one(
        comodel_name='hr.hospital.doctor',
        readonly=True
    )


    @api.onchange('doctor_id')
    def _onchange_doctor_set_mentor(self):
        if self.doctor_id and self.doctor_id.is_intern:
            if self.doctor_id.mentor_id:
                self.mentor_id = self.doctor_id.mentor_id
                return {
                    'warning': {
                        'title': _("Intern Doctor"),
                        'message': _(
                            "Selected doctor is an intern. Mentor was automatically assigned."
                        )
                    }
                }



    approved_date = fields.Datetime()

    severity = fields.Selection(
        selection=[
            ('light', 'Light'),
            ('medium', 'Medium'),
            ('hard', 'Hard'),
            ('critical', 'Critical'),
        ])
    def action_approve_by_mentor(self):
        for record in self:
            record.write({
                'approved': True,
                'approved_date': fields.Datetime.now()
            })