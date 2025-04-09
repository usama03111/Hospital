
# here we study how to generate a pdf report using parser file ------>

from odoo import api ,  models , fields

class AllPatientReport(models.TransientModel):
    # the report syntax will be like these
    # _name = "report.module name.template name"

    _name = "report.us_hospital.report_all_patient_list"
    _description = 'Patient Report'

    @api.model
    def _get_report_values(self , docids , data=None):
        print("data---------->" , data)
        print("docids---------->" , docids)
        domain = []

        gender = data.get('form_data').get('gender')
        if gender:
            domain += [('gender' , '=' , gender)]

        age = data.get('form_data').get('age')
        if age != 0 :
            domain +=[('age' , '=' , age)]

        docs = self.env['hospital.patient'].search(domain)
        print('domain--------------->>>>', domain)
        return {
            'docs': docs,
            'email': 'usamakhan03169690@gmail.com'
        }


# from here i will print the (report_patient_detail) template
class PatientDetailReport(models.AbstractModel):
    _name = "report.us_hospital.report_patient_detail"
    _description = 'Patient Details Report'

    @api.model
    def _get_report_values(self, docids, data=None):
        # docs = self.env['hospital.patient'].search([])
        # the docids return the id of the current object
        docs = self.env['hospital.patient'].browse(docids)
        print("docs",docs)
        return {
            'docs': docs,
        }