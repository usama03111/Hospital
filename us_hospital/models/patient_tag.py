from email.policy import default

from pkg_resources import require

from  odoo import api , fields , models , _

class PatientTag(models.Model):
    _name = "patient.tag"
    _description = "for tag"

    name = fields.Char(string="Name" , required=True)
    active = fields.Boolean(string="Active" , default=True , copy=False)  #the value will not be copied due to "copy=False"
    color = fields.Integer(string='Color')
    color_2 = fields.Char(string='Color2')
    sequence = fields.Integer(string="Sequence")

    def copy(self, default=None):
        if default is None:
            default={}
        if not default.get("name"):
            # default["name"] = (_("%s (copy)",self.name))
            default["name"] = self.name + " (copy)"
        return super(PatientTag,self).copy(default)

    #82 SQL constrains
    _sql_constraints = [
        (
        'unique_tag_name', 'unique (name,active)','Name must be unique.'),
        ('check_sequence' , 'check (sequence > 0)', "sequence must be non zero or a positive number")
    ]