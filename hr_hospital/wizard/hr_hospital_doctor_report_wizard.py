from odoo import models, fields, _
from odoo.exceptions import UserError

class DoctorReportWizard(models.TransientModel):
    _name = 'hr.hospital.doctor.report.wizard'
    _description = 'Doctor Report Wizard'

    doctor_ids = fields.Many2many(
        comodel_name='hr.hospital.doctor',
        string='Doctors',
        required=True,
    )

    def action_print_report(self):
        self.ensure_one()
        if not self.doctor_ids:
            raise UserError(_('Please select at least one doctor.'))

        return self.env.ref('hr_hospital.action_report_doctor_card').report_action(self.doctor_ids)

    def action_preview_report(self):
        self.ensure_one()
        if not self.doctor_ids:
            raise UserError(_('Please select at least one doctor.'))

        action = self.env.ref('hr_hospital.action_report_doctor_card').read()[0]
        action['report_type'] = 'qweb-html'
        # Pass the IDs to the action, similar to report_action()
        action['context'] = dict(self.env.context, active_ids=self.doctor_ids.ids)
        return action
