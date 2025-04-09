
from  odoo import api,fields , models

class SearchAppointmentWizard(models.TransientModel):
    _name = 'search.appointment.wizard'
    _description = 'search the appointments'

    search_patient = fields.Many2one('hospital.patient' , string='Patient Name')

    def action_search_appointment_m1(self):
        action = self.env.ref('us_hospital.action_hospital_appointment').read()[0]
        action['domain'] = [('patient_id' , '=' , self.search_patient.id)]
        return  action

    def action_search_appointment_m2(self):
        action = self.env['ir.actions.actions']._for_xml_id("us_hospital.action_hospital_appointment")
        action['domain'] = [('patient_id', '=', self.search_patient.id)]
        return action

    def action_search_appointment_m3(self):
        return {
            'name': 'Appointments',
            'type': 'ir.actions.act_window',
            'res_model': 'hospital.appointment',
            'view_type': 'form',
            'domain': [('patient_id', '=', self.search_patient.id)],
            'view_mode': 'tree,form',
            'target': 'current',
        }

