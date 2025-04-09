# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name' : 'Hospital Management',
    'version' : '17.0.1.0.0',
    'summary': 'Hospital Management Software',
    'author': 'Usama Wazir',
    'sequence': -100,
    'description': """Hospital Management Software""",
    'category': 'Productivity',
    'website': 'https://www.odoomates.tech',
    'license' : 'LGPL-3',
    'depends' : ['sale','mail' , 'product'],
    'data': [
        'security/ir.model.access.csv',
        'security/model_hospital_security_access.xml',
        'data/data.xml',
        'data/patient_tag_data.xml',
        'data/patient.tag.csv',
        'data/mail_template_data.xml',
        'wizard/search_appointment_view.xml',
        'wizard/create_appointment_view.xml',
        'wizard/appointment_report_view.xml',
        'wizard/all_patient_report_view.xml',
        'wizard/cancel_appointment_view.xml',
        'views/doctor_view.xml',
        # 'views/sale.xml',
        'views/partner.xml',
        'views/patient_view.xml',
        'views/kids_view.xml',
        'views/patient_gender_view.xml',
        'views/appointment_view.xml',
        'views/patient_tag_view.xml',
        'views/menu.xml',
        'views/odoo_playground_view.xml',
        # 'views/res_config_settings_views.xml',
        'views/lab.xml',
        'views/website_form.xml',
        'views/patient_template.xml',
        'report/report.xml',
        'report/appointment_details.xml',
        'report/patient_card.xml',
        'report/patient_detail.xml',
        'report/all_patient_list.xml',
    ],
    'demo': [],
    'qweb':[],
    'installable': True,
    'application': True,
    'auto_install':False,
}




