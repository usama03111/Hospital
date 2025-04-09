from email.policy import default
import random
from pydoc import browse

from passlib.handlers.sha2_crypt import sha512_crypt
from pkg_resources import require
import datetime

from reportlab.lib.randomtext import subjects

from odoo import api, fields, models, _
# from odoo.addons.test_impex.tests.test_load import message
from odoo.api import ondelete
from odoo.exceptions import ValidationError
from odoo.tools.safe_eval import module


class HospitalAppointment(models.Model):
    _name = "hospital.appointment"
    # this is only for messaging purposes & long notes
    # _inherit = ["mail.thread"]
    _inherit = ['mail.thread', 'mail.activity.mixin']  # mail.thread for sending email and mail.activity.mixin for showing activity in the form view
    _description = "hospital appointment"
    _rec_name = 'patient_id'
    # _order = 'serial_no desc'  #used to show the record in descending form
    _order = 'serial_no desc '  #the age will be not sorted because it is a related field

    @api.model
    def default_get(self, fields_list):
        res = super(HospitalAppointment,self).default_get(fields_list)
        if not res.get('date_appointment'):
            res['date_appointment'] = datetime.date.today()
        appointment_lines = []
        product_rec = self.env['product.product'].search([])
        for pro in product_rec:
            line = (0,0, {
                'name':pro.id,
                'qty':2,
            })
            appointment_lines.append(line)
        res.update({
            'prescription_line_ids':appointment_lines,
            'patient_id':18,
        })
        return res

    # Adding the sequential field to generate the serial numbers
    serial_no = fields.Char(string="Order Reference", required=True, copy=False,
                            readonly=True, default=lambda self: _("New"))
    # ondelete='cascade' during these the record will be deleted in these model but using ondelete='restrict' the record will not be deleted
    patient_id = fields.Many2one('hospital.patient', string='Patient',required=True ,
                                 ondelete='cascade' , tracking=1)
    patient_name_id = fields.Many2one('hospital.patient', string='Patient Name',)
    # add these field for return the picture
    users = fields.Many2one('res.users', string='company users',)
    # to add related field through which we can access the age field inside the 'hospital.patient' model
    age = fields.Integer(string="Age",related='patient_id.age' ,tracking=3) #if i used store=True it will store the age field in database

    state = fields.Selection([('draft', 'Draft'), ('confirm', 'Confirmed'),
                              ('done', 'Done'), ('cancel', 'Cancelled')],
                             String="Status", default='draft', tracking=7)
    # add the doctor field
    doctor_id = fields.Many2one('hospital.doctor', string='Doctor', required=True ,
                                help="select the doctor for a patient" , tracking=2)
    doctor_ids = fields.Many2many('hospital.doctor','hospital_patient_rel',
                                  'appointment_id','doctor_id_rec',
                                  string="Doctors" , )
    prescription = fields.Html(string='Prescription' , )
    priority = fields.Selection([
        ('0', 'Very Low'),
        ('1', 'Low'),
        ('2', 'Normal'),
        ('3', 'High')], string='Priority')

    # adding One2many field
    prescription_line_ids = fields.One2many('appointment.prescription.lines' ,'appointment_id',
                                            string='Prescription Lines')
    total_amount = fields.Monetary(string='Total Amount', compute='_compute_total_amount', currency_field='currency_id',)

    @api.depends('prescription_line_ids.price_subtotal')
    def _compute_total_amount(self):
        for record in self:
            # record.total_amount = sum(line.price_subtotal for line in record.prescription_line_ids)
            # Or using these methode
            total = 0.0
            for line in record.prescription_line_ids:
                total += line.price_subtotal
            record.total_amount = total

    hide_sales_price = fields.Boolean(string='Hide Sale Price')

    gender = fields.Selection([
        ("male", "Male"),
        ("female", "Female"),
        ("other", "other"),
    ],string='Gender')
    note = fields.Text(string="Description")
    # how to add date and time
    date_appointment = fields.Date(string="Date" , tracking=4)
    date_checkup = fields.Datetime(string="Date Check Up" ,tracking=5)
    duration = fields.Float(string="Duration" ,tracking=6)
    # 132 create a monetory field
    company_id = fields.Many2one('res.company',string='Company' ,default=lambda self:self.env.company)
    currency_id = fields.Many2one('res.currency', related='company_id.currency_id')
    # here we create the progress widget in odoo
    progress = fields.Integer(string='Progress' , compute='_compute_progress')

    # product_id = fields.Many2one('product.template',string='Product Template')
    # @api.onchange('product_id')
    # def onchange_product_id(self):
    #     for rec in self:
    #         lines=[(5, 0, 0)]
    #         for line in self.product_id.product_variant_ids:
    #             vals = {
    #                 'name': line.id,
    #                 'qty':5,
    #             }
    #             lines.append((0, 0, vals))
    #         rec.prescription_line_ids = lines
    #         print("self_product", lines)

    # this will return the rainbow
    def action_confirm(self):
        self.state = 'confirm'
        return {
            'effect': {
                'fadeout': 'slow',
                'message': "Appointment have been confirm successfully",
                'type': 'rainbow_man',
            }
        }

    def action_done(self):
        self.state = 'done'

    def action_draft(self):
        self.state = 'draft'
        # return {
        #     'warning': {
        #         'fadeout': 'slow',
        #         'title': "Invalid Quantity",
        #         'message': "Quantity must be a positive integer.",
        #     }
        # }

    def action_cancel(self):
        self.state = 'cancel'

    # here we assign the serial numbers to the field inside one2many
    def set_line_number(self):
        sl_no = 0
        for line in self.prescription_line_ids:
            sl_no +=1
            line.sl_no = sl_no
        return

    @api.model
    def create(self, values):
        if not values.get('note'):
            values['note'] = 'New Patient'
        # add the code for sequential field
        # If the serial field is not provided or is set to 'New', the condition becomes true.
        if values.get('serial_no', _('New')) == _('New'):
            # This fetches the next number in the sequence defined for the sequence with code 'hospital.patient'.
            values['serial_no'] = self.env['ir.sequence'].next_by_code('hospital.appointment') or _('New')
        res = super(HospitalAppointment, self).create(values)  # Create the record
        # here we assign the serial numbers to the field inside one2many
        res.set_line_number()   # Call the method on the newly created record
        # Return the newly created record
        return res

    # here we assign the serial numbers and also assign in create methode to the field inside one2many
    def write(self, vals):
        res = super(HospitalAppointment, self).write(vals)    # Update the records
        self.set_line_number()    # Call the method on the updated records (self)
        return res

    # When the value of patient_id is updated (e.g., the user selects a different patient in the form), the method onchange_patient_id is triggered.
    @api.onchange('patient_id')
    def onchange_patient_id(self):
        if self.patient_id:  # Check if patient_id is set
            if self.patient_id.gender: # Check if patient has a gender
                self.gender = self.patient_id.gender  # Assign patient's gender to current record's gender
            if self.patient_id.note:
                self.note = self.patient_id.note
        else:
            self.gender = ''
            self.note = ''

    def unlink(self):
        for rec in self:
            if rec.state == "done":
                raise ValidationError( _("you cannot delete %s as it is in Done state"% self.serial_no)) #the %s show the serial_no
            return super(HospitalAppointment,self).unlink()

    #here we add the function for  url button
    # def action_url(self):
    #     return {
    #         'type': 'ir.actions.act_url',
    #         'target': 'new',
    #         'url': 'https://chatgpt.com/',
    #     }

    # Or You Can also write these
    # def action_url(self):
    #     module_name = 'chatgpt.com'
    #     return {
    #         'type': 'ir.actions.act_url',
    #         'target': 'new',
    #         'url': 'https://%s/'%module_name,
    #     }

    # OR
    def action_url(self):
        # return {
        #     'type': 'ir.actions.act_url',
        #     'target': 'new',
        #     'url': 'https://apps.odoo.com/apps/modules/18.0/%s/'%self.prescription,
        # }

        '''
        check_record = self.env['hospital.appointment'].search([('id' , '=' , 2)])
        check_record_age = self.env['hospital.appointment'].search([]).sorted(key='age' , reverse=True).mapped('age')
        check_record_filter = self.env['hospital.appointment'].search([]).filtered(lambda s:s.gender == 'female')
        check_without_arbic = self.env['hospital.appointment'].search([]).mapped('patient_id.name')
        check_consist_arbic = self.env['product.template'].with_context(lang='ar_001').search([]).mapped('name')
        print('names of patients' , check_record.mapped('patient_id.name'))
        print('sorted partners' , check_record.sorted(lambda o:o.write_date ))
        print('filter partners' , check_record.filtered(lambda o: not o.hide_sales_price))
        print('Display Name' , check_record.display_name)
        print('Display check_record_filter' , check_record_filter)
        print('Display check_record_age' , check_record_age)
        print('Display check_without_arbic' , check_without_arbic)
        print('Display check_consist_arbic' , check_consist_arbic) '''

        search = self.env['hospital.appointment'].search([('patient_id' , '=',18)])
        print("id", search)
        for rec in search:
            print("search", rec.patient_id.name)
        filtered = self.env['hospital.patient'].search([]).filtered(lambda s:s.gender == 'female')
        print("Filtered",filtered)
        # search = self.env['hospital.patient'].search([('gender' , '=', 'male')])
        # search = self.env['hospital.patient'].search_count([('gender' , '=', 'male')])
        # browse = self.env['hospital.patient'].browse([1,2]).mapped('name')


        # browse = self.env['hospital.patient'].browse([1,2])
        # print("search browse",browse)
        # if browse.exists():
        #     print("result Exists")
        # else:
        #     print("Not Exists")

    # here we add the whatsapp button
    def action_share_whatsapp(self):
        if not self.patient_id.phone:
            raise ValidationError(_("Missing phone number in the patient record"))
        # message =  'Hi *%s*, your *appointment* number is: %s , Thank You' % (self.patient_id.name , self.serial_no)
        message = f"Hi *{self.patient_id.name}*, your *appointment* number is: {self.serial_no}, Thank You"
        self.message_post(body=message , subject="WhatsApp Message")   # due to this the message will print in the activity view
        # whatsapp_api_url = 'https://api.whatsapp.com/send?phone=%s&text=%s'%(self.patient_id.phone,message)
        whatsapp_api_url = f'https://api.whatsapp.com/send?phone={self.patient_id.phone}&text={message}'
        return{
            'type': 'ir.actions.act_url',
            'target': 'new',
            'url': whatsapp_api_url
        }

    def action_share_mail(self):
        template = self.env.ref("us_hospital.appointment_mail_template")
        for rec in self:
            if rec.patient_id.email:
                email_values= {'subject': 'Test Email'}
                template.send_mail(rec.id ,force_send=True , email_values= email_values)

    @api.depends('state')
    def _compute_progress(self):
        for rec in self:
            if rec.state == 'draft':
                progress = random.randrange(0,25)
            elif rec.state == 'confirm':
                progress = random.randrange(26,89)
            elif rec.state == 'done':
                progress = 100
            else:
                progress = 0
            rec.progress = progress

    #157 display notification
    def action_notification(self):
        message = "button click successfully"
        action = self.env.ref("us_hospital.action_hospital_patient")
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Click to open the patient record'),
                'message': "%s" ,
                'type': 'info',
                'links': [{
                    'label': self.patient_id.name,
                    'url': f'#action={action.id}&id={self.patient_id.id}&model=hospital.patient'
                }],

                'sticky': False,   #True/False will display for few seconds if false
                # due to  'next': dictionary we will be redirected to the form view
                # 'next': {
                #     'type': 'ir.actions.act_window',
                #     'res_model': 'hospital.patient',
                #     'res_id': self.patient_id.id,
                #     'views': [(False , 'form')],
                # }
            }
        }

# here we create a new model
class AppointmentPrescriptionLines(models.Model):
    _name = "appointment.prescription.lines"
    _description = "Appointment Prescription Lines"

    sl_no = fields.Integer(string='SNO.')
    name = fields.Many2one('product.product' , string='Medicine' , required=True)
    price = fields.Float(related='name.lst_price' , string='Price' , digits='Product Price')
    qty = fields.Integer(string='Quantity')
    appointment_id = fields.Many2one('hospital.appointment',string='Appointment')
    currency_id = fields.Many2one('res.currency', related='appointment_id.currency_id')
    # Before adding a monetary field we should, must have adding a res.currency field
    price_subtotal = fields.Monetary(string='Subtotal' , compute='_compute_price_subtotal' ,
                                     currency_field='currency_id')
    @api.depends('price','qty')
    def _compute_price_subtotal(self):
        for rec in self:
            rec.price_subtotal = rec.price * rec.qty
