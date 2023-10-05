# -*- coding: utf-8 -*-

import random
from datetime import timedelta
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


def _default_date():
    today = fields.Date.today()
    default_date = today + timedelta(days=90)
    return default_date


class RealEstate(models.Model):
    _name = 'real.estate'
    _inherit = ['mail.thread', 'mail.activity.mixin',]
    _description = 'Real Estate'
    _order = "state, id desc"
    _rec_name = "name"
    name = fields.Char(required=True, string="Title", tracking=True)
    property_type_id = fields.Many2one('estate.property.type', tracking=True, ondelete='cascade')
    description = fields.Text(tracking=True)
    postcode = fields.Char(tracking=True)
    date_availability = fields.Date(default=lambda self: _default_date())
    expected_price = fields.Float(tracking=True)
    selling_price = fields.Float(string="Selling Price", readonly=True, tracking=True)
    bedrooms = fields.Integer(default=2, tracking=True)
    living_area = fields.Integer(string="Living Area(sqm)", tracking=True)
    facades = fields.Integer(tracking=True)
    garage = fields.Boolean()
    garden = fields.Boolean()
    tag_ids = fields.Many2many('property.type.tag', tracking=True, ondelete='cascade')
    garden_area = fields.Integer(string="Garden Area(sqm)", tracking=True)
    garden_orientation = fields.Selection([('north', 'North'), ('south', 'South'), ('east', 'East'), ('west', 'West')],
                                          tracking=True)
    active = fields.Boolean(default=False, tracking=True)
    state = fields.Selection([
        ('new', 'New'),
        ('offer_received', 'Offer Received'),
        ('offer_accepted', 'Offer Accepted'),
        ('sold', 'Sold'),
        ('cancel', 'Cancelled')],
        string="Status", tracking=True, default='new', readonly=True)
    sales_person = fields.Many2one('res.users', string="Salesman", default=lambda self: self.env.user, tracking=True,
                                   ondelete='cascade')
    sales_person_email = fields.Char(string="Seller_Email", related='sales_person.email', tracking=True)
    sale_buyer = fields.Many2one('res.partner', string="Buyer", tracking=True, ondelete='cascade')
    sale_buyer_email = fields.Char(string='Buyer Mail')
    offer_ids = fields.One2many('estate.property.offer', 'property_id', ondelete='cascade', store=True)
    total_area = fields.Integer(string="Total Area(sqm)", compute='_compute_total_area', tracking=True, readonly=True,
                                store=True)
    best_offer = fields.Float(compute='_compute_best_offer', string="Best Offered", readonly=True, deafult=0.0,
                              store=True)
    progress = fields.Integer(string="progress", compute="_compute_progress", store=True)
    price = fields.Float(related='offer_ids.price')  # For Demonstrate > Not Uses
    image = fields.Image(string="Upload Property Image")

    '''Agents Detils Fields'''
    agent_id = fields.Many2one('agent.view', string="Agent", ondelte='cascade', tracking=True)
    agent_mail = fields.Char(string="Agent mail Id", related="agent_id.agent_mail", tracking=True)
    agent_address = fields.Char(string="Agent Address", related='agent_id.agent_address', tracking=True)
    agent_phone = fields.Char(string="Agent Phone:", related='agent_id.agent_phone', tracking=True)
    agent_pic = fields.Image(string="Agent Image", related='agent_id.agent_pic', tracking=True)
    sell_month_expected = fields.Selection([
        ('days', 'Within 15days'),
        ('1month', 'Within 1Month'),
        ('2month', 'Within 2Month'),
        ('3month', 'More-Than 3month'),
    ])
    password = fields.Char(string="Password")

    '''below field For smart button '''
    count_offer = fields.Integer(compute="_compute_count_offer", store=True)
    whatsapp_chat = fields.Char(compute="_compute_whatsapp_chat")
    count_tags = fields.Integer(compute="_compute_count_tags")
    invoice = fields.Char(compute="_compute_invoice")
    model_viewer_pic = fields.Binary(string='3D Model Rendering',store=True)


    def action_solds(self):
        for rec in self:
            if rec.state == 'cancel':
                raise ValidationError(_("Operation not possible to sold in Cancel state"))
            else:
                return {
                    'res_model': 'real.estate',
                    'res_id': rec.id,
                    'view_id': self.env.ref('real_estate.view_advertise_form').id,
                    'context': {'default_password': rec.password},
                }

    def action_verify_password(self):
        pswd = "admin"
        for rec in self:
            entered_password = rec.password
            if entered_password == pswd:
                rec.state = 'sold'
                return {
                    'effect': {
                        'fadeout': 'slow',
                        'message': "Congratulations! Property has been Sold!",
                        'type': 'rainbow_man',
                    }
                }
            else:
                raise ValidationError(_("Incorrect Credential Entered!!"))
        return True

    @api.depends('living_area', 'garden_area')
    def _compute_total_area(self):
        total = 0
        for rec in self:
            total = rec.living_area + rec.garden_area
        self.total_area = total

    #  1st way for check maximum best offer give by Clients(Create Button Not Work When it apply)
    # @api.depends('offer_ids.price')
    # def _compute_best_offer(self):
    #     for rec in self:
    #         self.best_offer = max(rec.offer_ids.mapped('price'))

    # 2nd way for check maximum best offer give by Clients
    @api.depends('offer_ids.price')
    def _compute_best_offer(self):
        com = 0.0
        for rec in self.offer_ids:
            if rec.price > com:
                com = rec.price
        self.best_offer = com

    @api.onchange('garden')
    def _onchange_garden(self):
        for rec in self:
            if rec.garden == 1:
                self.garden_area = 10
                self.garden_orientation = "north"
            if rec.garden == 0:
                self.garden_area = 0
                rec.garden_orientation = False

    def action_cancel(self):
        for rec in self:
            if self.state == 'sold':
                raise ValidationError(_("You can not Cancel a Property After Sold!!"))
            else:
                self.state = 'cancel'
        return True

    def action_reset_new(self):
        for rec in self:
            if self.state != 'cancel':
                raise ValidationError(_("RESET is Possible only in Cancel State"))
            else:
                self.state = 'new'
        return True

    def action_offer_received(self):
        for rec in self:
            if self.state in ['sold', 'cancel']:
                raise ValidationError(_("You can not Cancel a Property After Sold!!"))
            else:
                self.state = 'offer_received'
        return True

    def action_offer_accept(self):
        for rec in self:
            if self.state in ['sold', 'cancel']:
                raise ValidationError(_("You can not Cancel a Property After Sold!!"))
            else:
                self.state = 'offer_accepted'
        return True

    @api.constrains('postcode')
    def check_postcode(self):
        for rec in self:
            if len(rec.postcode) != 6:
                raise ValidationError(_("INVALID POSTCODE ,\n Please Enter Correct Postcode"))

    @api.constrains('expected_price')
    def check_expected_price(self):
        for rec in self:
            if rec.expected_price <= 0:
                raise ValidationError(_("WARNING....Expected Price Must be Positive Number!!🚫"))

    def unlink(self):
        for rec in self:
            if rec.state not in ['new', 'cancel']:
                raise ValidationError(_("WARNING....\n Deletion is possible only in New or Cancel State"))
            return super(RealEstate, self).unlink()

        # whatsapp_Chat

    def action_share_whatsapp(self):
        if not self.agent_id.agent_phone:
            raise ValidationError('Sorry! Missing Phone Number for agent')
        message = 'Hi! *%s* ,You have assigned To a New Property *%s*\n Please check Your Profile for more Info.' % (
            self.agent_id.agent_name, self.name)
        whatsapp_api_url = 'https://api.whatsapp.com/send?phone=%s&text=%s' % (self.agent_id.agent_phone, message)
        self.message_post(body=message, subject="whatsapp Message")
        return {
            'type': 'ir.actions.act_url',
            'target': 'new',
            'url': whatsapp_api_url
        }

    @api.depends('state')
    def _compute_progress(self):
        for rec in self:
            if rec.state == 'new':
                progress = random.randrange(1, 25)
            elif rec.state == 'offer_received':
                progress = random.randrange(25, 50)
            elif rec.state == 'offer_accepted':
                progress = random.randrange(50, 75)
            elif rec.state == "sold":
                progress = 100
            else:
                progress = 0
            rec.progress = progress

    @api.model
    def create(self, vals):
        if not vals.get('state'):
            vals['state'] = 'offer_received'
        return super(RealEstate, self).create(vals)

    @api.depends('agent_phone')
    def _compute_whatsapp_chat(self):
        for rec in self:
            if rec.agent_phone:
                self.whatsapp_chat = "Available"
            else:
                self.whatsapp_chat = "Unavailable"

    @api.depends('tag_ids')
    def _compute_count_tags(self):
        # local = 0
        for rec in self:
            result = len(rec.tag_ids)
        self.count_tags = result

    @api.depends('offer_ids.partner_id')
    def _compute_count_offer(self):
        for rec in self:
            rec.count_offer = self.env['estate.property.offer'].search_count([('property_id', '=', rec.id)])

    @api.depends('state')
    def _compute_invoice(self):
        for rec in self:
            if rec.state == 'sold':
                self.invoice = 'Created'
            else:
                self.invoice = 'UnCreated'

    def action_count_offer(self):
        return {
            'name': _('Total Offered'),
            'view_mode': 'list',
            'type': 'ir.actions.act_window',
            'domain': [('property_id', '=', self.id)],
            'res_model': 'estate.property.offer',
            'target': 'current',
        }

    def action_whatsapp_chat(self):
        if not self.agent_id.agent_phone:
            raise ValidationError('Sorry! Missing Phone Number for agent')
        message = 'Hi! *%s* ,I hope you are Doing Well' % (self.agent_id.agent_name)
        whatsapp_api_url = 'https://api.whatsapp.com/send?phone=%s&text=%s' % (self.agent_id.agent_phone, message)
        self.message_post(body=message, subject="whatsapp Message")
        return {
            'type': 'ir.actions.act_url',
            'target': 'new',
            'url': whatsapp_api_url
        }

    def action_count_tags(self):
        return {
            'name': _('Tags'),
            'view_mode': 'list',
            'type': 'ir.actions.act_window',
            # 'domain': [('tag_ids', 'in', self.id)],
            'res_model': 'property.type.tag',
            'target': 'current',
        }

    def action_invoice_status(self):
        if self.state == 'sold':
            return {
                'name': _('Invoice'),
                'view_mode': 'list,form',
                'type': 'ir.actions.act_window',
                'res_model': 'account.move',
                'target': 'current',
            }
        else:
            raise ValidationError(_("Invoice Not Created for this Property!!🛑"))

    def send_email(self):
        self.ensure_one()
        ir_model_data = self.env["ir.model.data"]
        template_id = ir_model_data.env.ref("real_estate.email_estate_view")
        try:
            compose_form_id = ir_model_data.env.ref(
                "mail.email_compose_message_wizard_form"
            )
        except ValueError:
            compose_form_id = False

        mail_notification_layout = (
            "mail.mail_notification_layout_with_responsible_signature"
        )

        ctx = dict(self.env.context or {})
        ctx.update(
            {
                "default_model": "real.estate",
                "active_model": "real.estate",
                "active_id": self.ids[0],
                "default_res_id": self.ids[0],
                "default_use_template": bool(template_id),
                "default_template_id": template_id.id,
                "default_composition_mode": "comment",
                "default_email_layout_xmlid": mail_notification_layout,
                "force_email": True,
                "mark_rfq_as_sent": True,
            }
        )
        lang = self.env.context.get("lang")
        if {"default_template_id", "default_model", "default_res_id"} <= ctx.keys():
            template = self.env["mail.template"].browse(ctx["default_template_id"])
            if template and template.lang:
                lang = template._render_lang([ctx["default_res_id"]])[
                    ctx["default_res_id"]
                ]

        self = self.with_context(lang=lang)
        if self.state in ["new", "sold"]:
            ctx["model_description"] = _("Request for Quotation")
        else:
            ctx["model_description"] = _("Sale Order")

        return {
            "name": _("Compose Email"),
            "type": "ir.actions.act_window",
            "view_mode": "form",
            "res_model": "mail.compose.message",
            "views": [(compose_form_id.id, "form")],
            "view_id": compose_form_id.id,
            "target": "new",
            "context": ctx,
        }


"""forPrint PDF report through custom button created"""
# def print_reports(self):
#     return self.env.ref('real_estate.action_report_property').report_action(self)
