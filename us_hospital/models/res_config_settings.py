# -*- coding: utf-8 -*-

from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'


    cancel_days = fields.Integer(string="Cancel Days" , config_parameter="us_hospital.cancel_days")