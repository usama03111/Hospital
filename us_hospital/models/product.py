from pkg_resources import require

from odoo import api, fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    detailed_type = fields.Selection(selection_add=[
        ('test', 'Test'),('service' ,)  # here i used service because i want a Test before Service
    ], tracking=True, ondelete={'test': 'set default'})




