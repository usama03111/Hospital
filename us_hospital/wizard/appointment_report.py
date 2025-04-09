
from odoo import api , models , fields

class AppointmentReportWizard(models.TransientModel):
    _name = 'appointment.report.wizard'
    _description = 'Print Appointment Wizard'

    patient_id = fields.Many2one('hospital.patient' , string='Patient')
    date_from = fields.Date(string="Date From")
    date_to = fields.Date(string="Date To")


    # here we create a function for report excel button to pass a data into the (patient_appointment_xls.py) file
    def action_print_excel_report(self):
        domain = []
        patient_id = self.patient_id
        if patient_id:
            domain += [('patient_id', '=', patient_id.id)]
        date_from = self.date_from
        if date_from:
            domain += [('date_appointment', '>=', date_from)]
        date_to = self.date_to
        if date_to:
            domain += [('date_appointment', '<=', date_to)]
        print("domain----", domain)
        # so it give us a filter records based on domain
        appointments = self.env['hospital.appointment'].search_read(domain)
        data = {
            "appointments": appointments,
            "form_data": self.read()[0],
        }
        print("appointments------------->>>" , appointments)
        return self.env.ref('us_hospital.report_patient_appointment_xlsx').report_action(self, data=data)




    def action_print_report(self):
        # here we set the filter to check the domain condition in hospital.appointment model
        domain = []
        patient_id = self.patient_id
        if patient_id:
            domain += [('patient_id' , '=' , patient_id.id)]
        date_from = self.date_from
        if date_from:
            domain += [('date_appointment' , '>=' , date_from)]
        date_to = self.date_to
        if date_to:
            domain += [('date_appointment' , '<=' , date_to)]
        print("domain----" , domain)

        # appointments = self.env['hospital.appointment'].search_read(domain)
        # data = {
        #     'form_data': self.read()[0],
        #     'appointments': appointments
        # }
        # print("appointments------>", appointments)
        # # here we specify the id of a report.action
        # return self.env.ref('us_hospital.action_report_appointments').report_action(self, data=data)
        # OR

        appointments = self.env['hospital.appointment'].search(domain)
        print("appointments------>",appointments)
        appointment_list = []
        for appointment in appointments:
            vals = {
                'serial_no': appointment.serial_no,
                'note': appointment.note,
                'age': appointment.age,
            }
            appointment_list.append(vals)
        data = {
            'form_data': self.read()[0],  #by using these you will take the detail of the current model
            # 'appointments': appointments
            'appointments': appointment_list
        }
        print("appointment_list------",appointment_list)
        print("self--------------------->",self.read()[0])
        # here we specify the id of a report.action
        return self.env.ref('us_hospital.action_report_appointments').report_action(self,data=data)
