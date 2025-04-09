from datetime import date
from datetime import date

from dateutil import relativedelta
from dateutil.utils import today
from pkg_resources import require

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class CreateAppointmentWizard(models.TransientModel):
    _name = "cancel.appointment.wizard"
    _description = "Cancel Appointment Wizard"


    @api.model
    def default_get(self, fields_list):
        res = super(CreateAppointmentWizard , self).default_get(fields_list)
        print("-----context", self.env.context)
        if self.env.context.get("active_id"):
            res['appointment_id'] = self.env.context.get("active_id")
        res['date_cancellation'] = date.today()
        return res

    date_cancellation = fields.Date(string='Cancellation Date', )
    # when the appointments are matching to these domain the appointments  will not be shown in the form view
    appointment_id = fields.Many2one('hospital.appointment', string='Patient', required=True ,
                                     domain=[('state','in',('done' , 'cancel' , 'draft')) , ('priority' , 'in' , (0,1,False))])
    reason = fields.Text( string='Reason')

    # how to access value from setting
    def action_cancel(self):
        cancel_day = self.env['ir.config_parameter'].get_param('us_hospital.cancel_days') #due to this function the days we will retrieve as a string
        print("cancel_day----",cancel_day)
        allowed_date = self.appointment_id.date_appointment - relativedelta.relativedelta(days=int(cancel_day))
        print("allowed_date----",allowed_date)
        # when the appointment date is lees than today date it will not be cancelled when the appointment date is greater 3 days from today date it will be cancelled
        if cancel_day !=0 and allowed_date < date.today():
            raise ValidationError(_("sorry cancellation is not allowed for these booking !"))
        self.appointment_id.state = "cancel"
        # with the help of these the cancel wizard will not be closed automatically
        return {
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'cancel.appointment.wizard',
            'target': 'new',
            'res_id': self.id,
        }
        # how to reload the screen automatically
        # return {'type': 'ir.actions.client',
        #         'tag': 'reload'}

