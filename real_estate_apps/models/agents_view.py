from datetime import timedelta
from odoo.exceptions import ValidationError
from odoo import models, fields, api, _
import random


class AgentView(models.Model):
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _name = 'agent.view'
    _description = 'Agent Commission View'
    _rec_name = "agent_name"
    reference = fields.Char(string='Agent ID', required=True, copy=False, readonly=True, default=lambda self: _('New'))

    # property_name=fields.Many2one('real.estate',ondelete='cascade',tracking=True)
    # property_id=fields.Many2one('estate.property.offer',ondelete='cascade',tracking=True)

    agent_property_id = fields.Many2one('estate.property.type', string="Property Involved:", required=True,
                                        tracking=True)
    agent_name = fields.Char(string="Agent", tracking=True)
    agent_mail = fields.Char(string="Agent mail Id", tracking=True)
    agent_address = fields.Char(string="Agent Address", tracking=True)
    agent_phone = fields.Char(string="Agent Phone:", tracking=True)
    agent_pic = fields.Image(string="Agent Image", tracking=True)
    agent_exp = fields.Selection([
        ('fresher', 'FRESHER'),
        ('less_one', 'Less Than 1 Yr'),
        ('one_two', 'EXP > 1 year'),
        ('three_four', 'EXP > 3Year'),
        ('professional', 'Professional'),
    ], string="Agent Experience", tracking=True)
    agent_type = fields.Selection([('full_time', 'Full Time'), ('part_time', 'Part Time'), ('intern', 'Intern')],
                                  string="Agent Type", default="full_time")
    agent_language_ids = fields.Many2many('agent.language', string="Agent Language Known", tracking=True,
                                          ondelete="cascade")
    agent_residential = fields.Selection(
        [
            ('east_india', 'BR-UP-MP'),
            ('west_india', 'HR-AP'),
            ('south_india', 'HYD-BNG-KER'),
            ('others', 'OTHERS'),
            ('foreign', 'FOREIGN'),
        ], string="Agent Residential"
    )

    agents_ids=fields.One2many('estate.property.offer','offer_agent_id', domain=[('status', 'in', ['accepted'])])
    efficiency = fields.Integer(string="Language Efficiency", compute='_compute_efficiency')
    proficient_level = fields.Selection([
        ('intermediate', 'Intermediate'),
        ('beginner', 'Beginner'),
        ('professional', 'Professional'),
    ], string="Language Efficiency", required=True, Tracking=True)
    agent_offers_ids = fields.One2many('real.estate', 'agent_id', ondelete='cascade', tracking=True)



    # For creating a Sequence Number
    @api.model
    def create(self, vals):
        vals['reference'] = self.env['ir.sequence'].next_by_code('agent.view')
        return super(AgentView, self).create(vals)

    @api.depends('proficient_level')
    def _compute_efficiency(self):
        for rec in self:
            if rec.proficient_level == 'intermediate':
                efficiency = random.randrange(45, 70)
            elif rec.proficient_level == 'beginner':
                efficiency = random.randrange(20, 45)
            elif rec.proficient_level == 'professional':
                efficiency = random.randrange(70, 100)
            else:
                efficiency = 0
            rec.efficiency = efficiency


class AgentLangauge(models.Model):
    _name = 'agent.language'
    _rec_name = 'language'
    _description = 'Agent Info'
    language = fields.Char(string="Language", required=True)
    active = fields.Boolean(string='Active', default=True)
    color = fields.Integer(string="Color")
