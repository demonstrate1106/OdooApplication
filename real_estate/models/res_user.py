from odoo import models, fields, api


class ResUser(models.Model):
    _inherit = 'res.users'
    property_ids = fields.One2many('real.estate', 'sales_person',
                                   domain=[('state', 'in', ['offer_received', 'offer_accepted'])])



