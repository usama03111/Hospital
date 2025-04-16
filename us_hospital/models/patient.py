from email.policy import default
from datetime import date

from dateutil import relativedelta
from dateutil.utils import today
from pkg_resources import require

from odoo import api, fields, models, _
from odoo.addons.test_convert.tests.test_env import field, record
from odoo.exceptions import ValidationError
from odoo.osv.expression import is_boolean
from odoo.tools.populate import compute


class HospitalPatient(models.Model):
    _name = "hospital.patient"
    # this is only for messaging purposes & long notes
    # _inherit = ["mail.thread"]
    _inherit = ['mail.thread','mail.activity.mixin']  # mail.thread for sending email and mail.activity.mixin for showing activity in the form view
    _description = "To manage the hospital patient"
    # _order = 'reference desc'  OR
    _order = 'id desc'

    name = fields.Char(string="Name", required=True, tracking=True)
    # Adding the sequential field to generate the serial numbers
    reference = fields.Char(string="Order Reference", required=True, copy=False,
                            readonly=True, default=lambda self: _("New"))
    age = fields.Integer(string="Age", tracking=True ,compute='_compute_age',
                         search='_search_age', inverse="_inverse_compute_age")
    date_of_birth = fields.Date(string='Date Of Birth')
    #A compute field will not store in the database
    @api.depends('date_of_birth')
    def _compute_age(self):
        for rec in self:
            today = date.today()
            if rec.date_of_birth:
                rec.age =  today.year - rec.date_of_birth.year
            else:
                rec.age = 0

    #99 how to define a inverse function for compute field
    @api.depends("age")
    def _inverse_compute_age(self):
        today = date.today()
        for rec in self:
            rec.date_of_birth = today - relativedelta.relativedelta(years=rec.age)

    #100 searchable non stored compute field
    def _search_age(self , operator , value):
        date_of_birth = date.today() - relativedelta.relativedelta(years=value)
        print("date_of_birth------", date_of_birth)
        start_of_year = date_of_birth.replace(day=1 , month=1)
        end_of_year = date_of_birth.replace(day=31 , month=12)
        return [("date_of_birth" , '>=' , start_of_year),("date_of_birth" , '<=' , end_of_year)]

    # OR searchable non stored compute field
    # def _search_age(self, operator, value):
    #     date_of_birth = date.today() - relativedelta.relativedelta(years=value)
    #     start_of_date = date_of_birth - relativedelta.relativedelta(years=1)
    #     print("start_of_date------", start_of_date)
    #     return [('date_of_birth', '>', start_of_date), ('date_of_birth', '<=', date_of_birth)]

    gender = fields.Selection([
        ("male", "Male"),
        ("female", "Female"),
        ("other", "other"),
    ],
        required=True, default="male", tracking=True)
    note = fields.Text(string="Description")

    # add one2many field which show the all appointments that can occur by patient in "hospital.appointment" model
    appointment_ids = fields.One2many('hospital.appointment', 'patient_id', string='Appointments')
    # add many2many field
    tag_ids = fields.Many2many('patient.tag' , 'hospital_patient_tag_rel','patient_id','tag_id_rec', string='Tags')
    # adding  many 2 one fields purposes is that to extract the data from the database/model
    partner_id = fields.Many2one('res.partner', String="Responsible", tracking=True)
    order_id = fields.Many2one('sale.order', String="Sale Order")

    # @api.onchange("partner_id")
    # def onchange_partner_id(self):
    #     for rec in self:
    #         return {'domain': {'order_id': [('partner_id', '=', rec.partner_id.id)]}}

    # compute Field and function (here we can specify the function name (compute='_compute_appointment_count'))
    appointment_count = fields.Integer(string="Appointment Count", compute='_compute_appointment_count' ,)

    parent = fields.Char(string='Parent')
    marital_status = fields.Selection([
        ('married' , 'Married'),
        ('single' , 'Single'),
    ],string="Marital Status" , tracking=True)
    partner_name = fields.Char(string='Partner Name')
    is_birthday = fields.Boolean(string='Birthday' , compute='_compute_is_birthday')
    phone = fields.Char(string="Phone")
    email = fields.Char(string="Email")
    website = fields.Char(string="Website")
    # these function will go to the database table of a (hospital.appointment)model and count the appointment occurring
    #here we add the depend field appointment_ids to recompute the total appointments
    # @api.depends('appointment_ids')
    # def _compute_appointment_count(self):
    #     for rec in self:  # the singleton error occur when we want to show
    #         # the field in the tree view to solve these error we using the for loop
    #         appointment_count = self.env['hospital.appointment'].search_count([('patient_id', '=', rec.id)])
    #         rec.appointment_count = appointment_count

    # use  Read Group Method to count the total 'confirm' appointments in the (hospital.appointment) model
    @api.depends('appointment_ids')
    def _compute_appointment_count(self):
            appointment_group = self.env['hospital.appointment'].read_group(domain=[] ,
                                                                              fields=['patient_id'] , groupby=['patient_id'])
            for appointment in appointment_group:
                patient_id = appointment.get('patient_id')[0]
                print("patient_id======",patient_id)
                # self.browse(patient_id) fetches a record from the self recordset (the current model's records) using the patient_id.
                patient_rec = self.browse(patient_id)
                print("patient_rec---------------------",patient_rec)
                # It updates the appointment_count field of the patient_rec (the fetched patient record) with a value from appointment['patient_id_count'].
                patient_rec.appointment_count = appointment['patient_id_count']
                # Remove the processed patient record from the current recordset (self)
                # to avoid updating it again in the final loop where remaining records are set to 0.
                self -= patient_rec
            self.appointment_count = 0


    image = fields.Binary(string='Patient Image')

    # the key will go to the database and the value will be shown to the user
    state = fields.Selection([('draft', 'Draft'), ('confirm', 'Confirmed'),
                              ('done', 'Done'), ('cancel', 'Cancelled')],
                             String="Status", default='draft', tracking=True)

    def action_confirm(self):
        for rec in self:
            rec.state = 'confirm'

    def action_done(self):
        self.state = 'done'

    def action_draft(self):
        self.state = 'draft'

    def action_cancel(self):
        self.state = 'cancel'

    # override the create method when we save any record the create method is executed
    @api.model
    def create(self, values):
        if not values.get('note'):
            values['note'] = 'New Patient'
        # add the code for sequential field
        # If the serial field is not provided or is set to 'New', the condition becomes true.
        if values.get('reference', _('New')) == _('New'):
            # This fetches the next number in the sequence defined for the sequence with code 'hospital.patient'.
            values['reference'] = self.env['ir.sequence'].next_by_code('hospital.patient') or _('New')
        # Call the original 'create' method of the parent class to actually create the record
        res = super(HospitalPatient, self).create(values)
        # Return the newly created record
        return res

    # here we can override the default function in odoo
    #  The default_get function gives us default value of a field when we click the 'Create' button in UI and we still can change that value before saving it.
    @api.model
    def default_get(self, fields_list):
        res = super(HospitalPatient, self).default_get(fields_list)
        return res

    @api.constrains("name")
    def _check_name(self):
        for rec in self:
            patients = self.env['hospital.patient'].search([("name", '=', rec.name), ("id", "!=", rec.id)])
            if patients:
                raise ValidationError(_("Name %s is already exist", rec.name))

    #at_uninstall=False due to these the function will not run during the uninstallation of the module
    @api.ondelete(at_uninstall=False)
    def _check_appointments(self):
        for rec in self:
            if rec.appointment_ids:
                raise (ValidationError(_("You cannot delete a patients with appointments...!")))

    @api.constrains("age")
    def _check_age(self):
        for rec in self:
            if rec.age == 0:
                raise (ValidationError(_("Age cannot be zero...!")) )

    @api.constrains("date_of_birth")
    def _check_date_of_birth(self):
        for rec in self:
            if rec.date_of_birth and rec.date_of_birth > date.today():
                raise ValidationError(_("The entered date of birth is not acceptable...!"))

    def name_get(self):
        result = []
        print("---context--",self.env.context)
        for rec in self:
            if self.env.context.get("show_code"):
                name = rec.name
            else:
                name = '[' + rec.reference + '] ' + rec.name
            result.append((rec.id, name))
        return result

    # this name search is used for search by both reference and name in many2one field
    @api.model
    def name_search(self, name='', args=None, operator='ilike', limit=100):
        if args is None:
            args = []
        domain = args+['|',('reference', operator,name),('name',operator , name)]
        return super(HospitalPatient,self).search(domain , limit=limit).name_get()

    @api.model
    def name_create(self, name):
        return self.create({'name': name}).name_get()[0]

    # OR
    # def name_get(self):
    #     return [(record.id , '[%s] ' '%s' % (record.reference , record.name))for record in self]

    #<!--Here we add the smart button -->
    def action_open_appointments(self):
        action = self.env.ref('us_hospital.action_hospital_appointment').read()[0]
        action['domain'] = [('patient_id' , '=' , self.id)]
        return action

    #OR
        # return {
        #     'name': 'Appointments',
        #     'type': 'ir.actions.act_window',
        #     'res_model': 'hospital.appointment',
        #     'context':  {'default_patient_id':self.id},
        #     'domain': [('patient_id', '=', self.id)],
        #     'view_mode': 'tree,form',
        #     'target': 'current',
        # }

    # these write methode is used when we update the record
    def write(self, vals):
        print("write methode is triggered",vals)
        # if not self.reference and vals.get('reference'):
        #     # This fetches the next number in the sequence defined for the sequence with code 'hospital.patient'.
        #     vals['reference'] = self.env['ir.sequence'].next_by_code('hospital.patient') or _('New')
        return super(HospitalPatient,self).write(vals)

    # these function is for testing a button which was added  for group in the tree view of hospital.appointment
    def test_group(self):
        print("test group")
        return

    # this function is for alert message to print the birthday
    @api.depends('date_of_birth')
    def _compute_is_birthday(self):
        for rec in self:
            is_birthday = False
            if rec.date_of_birth:
                today = date.today()
                if today.day == rec.date_of_birth.day and today.month == rec.date_of_birth.month:
                    is_birthday = True
        rec.is_birthday = is_birthday