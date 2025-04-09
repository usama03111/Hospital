from datetime import date

from pkg_resources import require

from odoo import api, fields, models, _


class CreateAppointmentWizard(models.TransientModel):
    _name = "create.appointment.wizard"
    _description = "Create Appointment Wizard"


    @api.model
    def default_get(self, fields_list):
        res = super(CreateAppointmentWizard , self).default_get(fields_list)
        print("-----context", self.env.context)
        if self.env.context.get("active_id"):
            res['patient_id'] = self.env.context.get("active_id")
        res['date_appointment'] = date.today()
        return res

    date_appointment = fields.Date(string='Date', )
    patient_id = fields.Many2one('hospital.patient', string='Patient', required=True , )
    doctor_id = fields.Many2one('hospital.doctor', string='Doctor', required=True)

    def action_create_appointment(self):
        vals = {
            'patient_id': self.patient_id.id,
            # 'doctor_id': 2,  #i can add these b/c error occur due to server action
            'doctor_id': self.doctor_id.id,  # Use .id to get the ID of the record -/how to set mandatory field 62
            'date_appointment': self.date_appointment
        }
        self.patient_id.message_post(body="Appointment Created Successfully" , subject='Appointment Creation')
        appointment_rec = self.env['hospital.appointment'].create(vals)
        # this will return the newly created record
        return {
            'name': ('Appointment'),
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'hospital.appointment',
            'res_id': appointment_rec.id,
            'target': 'new', #this will give you like a popup
        }

    # this button  will return the total appointments of a specific patient
    # def action_view_appointment(self):
    #     action = self.env.ref("us_hospital.action_hospital_appointment").read()[0]
    #     action['domain'] = [('patient_id' , '=' , self.patient_id.id)]
    #     return  action
