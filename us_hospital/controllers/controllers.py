# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request
from  odoo.addons.website_sale.controllers.main import WebsiteSale
from odoo.release import author


class Hospital(http.Controller):
    @http.route('/patient_webform', website=True ,auth='user',type="http")
    def patient_webform(self, **kw):
        return http.request.render("us_hospital.create_patient",{})

    @http.route('/create_webpatient', website=True, auth='public', type="http")
    def create_webpatient(self, **kw):
        print('------>', kw)
        request.env['hospital.patient'].sudo().create(kw)
        return http.request.render("us_hospital.patient_thanks",{})

    @http.route('/hospital/patient/',website=True ,auth='public')
    def hospital_patient(self,**kw):
        patients = request.env['hospital.patient'].sudo().search([])
        print('Patients',patients)
        return request.render('us_hospital.patient_page',{
            'patients':patients
        })


    '''@http.route('/create_webpatient', website=True, auth='public', type="http", csrf=False)
    def create_webpatient(self, **kw):
        # Debugging: Print the received data
        print("Received Data:", kw)

        # Map form field names to actual model fields
        patient_data = {
            "name": kw.get("patient_name"),  # Make sure 'name' is the correct field in hospital.patient
            "email": kw.get("email_id")  # Make sure 'email' is the correct field
        }

        # Ensure that required fields are present
        if not patient_data["name"] or not patient_data["email"]:
            return request.redirect('/patient_webform')  # Redirect back if required data is missing

        # Create the patient record
        request.env["hospital.patient"].sudo().create(patient_data)

        return http.request.render("us_hospital.patient_thanks", {})
'''

