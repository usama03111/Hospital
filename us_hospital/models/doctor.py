from email.policy import default

from pkg_resources import require

from  odoo import api, fields , models , _
from odoo.tools.populate import compute


class HospitalDoctors(models.Model):
    _name = 'hospital.doctor'
    _inherit = ['mail.thread' , 'mail.activity.mixin']
    _inherits = {'hospital.patient': 'related_patient_id'}
    _description = 'here to show the doctors data'
    _rec_name = 'doctor_name'
    _order = 'sequence ,id'

    related_patient_id = fields.Many2one('hospital.patient',string='Related Patient ID')
    doctor_name = fields.Char(string='Doctor Name' , required=True, tracking=True)
    age = fields.Integer(string='Age' , tracking=True , copy=False)
    # when we drag and drop the record the odoo will automatically change the sequence value of the record
    sequence = fields.Integer(string='Sequence' , default=10)
    gender = fields.Selection([
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other'),
    ],string='Gender' , required=True , default='male',tracking=True)
    # here we add the many2many for to show the total appointment of a doctor
    appointment_ids = fields.Many2many('hospital.appointment','hospital_patient_rel',
                                       'doctor_id_rec','appointment_id',string="Doctors")
    # 121 Here we create the reference field in odoo and store the data in the database in string form
    record = fields.Reference(selection=[('hospital.patient' , 'Patient'),
                                         ('hospital.appointment' , 'Appointment')],string='Record')
    user_id = fields.Many2one('res.users',string="Related User")
    note = fields.Text(string='Description')
    image = fields.Binary(string='Doctor Image')
    # here we count the appointments of a doctor
    appointment_count = fields.Integer(string='Appointment Count' , compute='_compute_appointment_count')
    def _compute_appointment_count(self):
        for rec in self:
            appointment_count = self.env['hospital.appointment'].search_count([('doctor_id' , '=' , rec.id)]) #if the doctor_id field is in hospital.appointment is equal to rec.id
            rec.appointment_count = appointment_count

    # we add these field for archive the record
    active = fields.Boolean(string='Active' , default=True , tracking=True)

    # override the duplicate function methode
    def copy(self , default=None):
        if default is  None:
            default = {}
            if not default.get('doctor_name'):
                default['doctor_name'] = _("%s (Copy)",self.doctor_name)
            default['note'] = 'Copied Record'

        return super(HospitalDoctors, self).copy(default)

    # when we don't have a _rec_name or name field in our model
    # @api.model
    # def name_create(self, name):
    #     print("name_create---------",name)
    #     return self.create({'doctor_name': name}).name_get()[0]