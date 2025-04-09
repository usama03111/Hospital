from  odoo import api, fields , models
from odoo.api import returns


class ResGroups(models.Model):
    _inherit = 'res.groups'

    @api.model
    def get_application_groups(self, domain):
        purchase_receipt = self.env.ref('account.group_purchase_receipts').id
        return super(ResGroups,self).get_application_groups(domain + [('id', '!=',purchase_receipt)])