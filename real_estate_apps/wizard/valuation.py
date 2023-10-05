from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class Propertyvaluation(models.TransientModel):
    _name = 'property.valuation'
    _description = 'Property valuation'

    Property_value_id = fields.Many2one('real.estate', string='Property Name')
    bedrooms = fields.Integer(related='Property_value_id.bedrooms', tracking=True, readonly=True)
    living_area = fields.Integer(related='Property_value_id.living_area', string="Living Area(sqm)", tracking=True,
                                 readonly=True)
    garden = fields.Boolean(related='Property_value_id.garage', string='Garden', readonly=True)
    total_area = fields.Integer(related='Property_value_id.total_area', string="Total Area(sqm)", tracking=True,
                                readonly=True)
    property_type_id = fields.Many2one(related='Property_value_id.property_type_id', tracking=True,
                                       ondelete='cascade', readonly=True)
    expected_price = fields.Float(related='Property_value_id.expected_price', tracking=True, readonly=True)
    tag_ids = fields.Many2many(related='Property_value_id.tag_ids', tracking=True, ondelete='cascade')
    evaluate_price = fields.Float(string="Valuated Price()", readonly=True, tracking=True)

    '''Price Evaluation in IND Rupees Code'''

    def action_valuate_property(self):
        per_sqm_price = 6460
        if self.living_area:
            self.evaluate_price = per_sqm_price * self.living_area

        else:
            self.evaluate_price = per_sqm_price * self.total_area

        return {
            'name': _('Price Evaluation for Specific Property Based on Living area Size'),
            'view_mode': 'form',
            'type': 'ir.actions.act_window',
            'res_id': self.id,
            'res_model': 'property.valuation',
            'target': 'new',
            'effect': {
                'fadeout': 'medium',
                'message': f"{self.evaluate_price} is Evaluated Price for \n this Property based on Living Area!!! ",
                'type': 'rainbow_man',
            }
        }

    '''Price Evaluation in USD Dollor $ - Code'''

    def action_valuate_property_dollor(self):
        per_sqm_price = 88
        if self.living_area:
            self.evaluate_price = per_sqm_price * self.living_area

        else:
            self.evaluate_price = per_sqm_price * self.total_area

        return {
            'name': _('Price Evaluation for Specific Property Based on Living area Size'),
            'view_mode': 'form',
            'type': 'ir.actions.act_window',
            'res_id': self.id,
            'res_model': 'property.valuation',
            'target': 'new',
            'effect': {
                'fadeout': 'medium',
                'message': f"\n\n\n {self.evaluate_price} $ is Evaluated Price for \n this Property based on Living "
                           f"Area!!! ",
                'type': 'rainbow_man',
            }
        }

    def action_close(self):
        return True
