# -*- coding: utf-8 -*-
import traceback

from odoo import api, fields, models, _, SUPERUSER_ID
import time
from odoo.exceptions import ValidationError
from datetime import datetime, timedelta
import requests
import json


class Customer(models.Model):
    _name = 'crm_voip.crm.customer'
    _rec_name = 'full_name'
    _description = 'CRM Customer'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = "id desc"

    partner_id = fields.Many2one(comodel_name='res.partner', string='Seller', domain=[('is_company', '=', True)],
                                 required=True, index=True)
    contact_id = fields.Many2one(comodel_name='res.partner', string='Contact')
    name = fields.Char("Name",  index=True)
    surname = fields.Char("Surname", index=True)
    birthdate = fields.Date('Birth Date', )
    sex = fields.Selection([('1', 'Male'), ('2', 'Female')], "Sex")
    sex_html = fields.Html("#", compute="_show_detail")
    nationality = fields.Selection([('1', 'TC'), ('2', 'Other')], "Nationality")
    note = fields.Char("Note")
    black_list = fields.Boolean("Black List", default=False)
    permit_communication = fields.Boolean("Permit Communication", default=False)
    source_id = fields.Many2one(comodel_name="crm_voip.crm.customer.source", string="Source", index=True)
    phone_ids = fields.One2many(comodel_name="crm_voip.crm.customer.phone", inverse_name="customer_id", string="Phones")
    call_ids = fields.One2many(comodel_name="crm_voip.crm.customer.call", inverse_name="customer_id", string="Calls")
    full_name = fields.Char("Full Name", compute='_compute_full_name', search='_search_fullname')
    questions_ids = fields.One2many(comodel_name="crm_voip.crm.customer.questions", inverse_name="customer_id",
                                    string="Questions")
    sms_ids = fields.One2many(comodel_name="crm_voip.sms.log", inverse_name="customer_id", string="Sms")


    # KANBAN
    kanban_last_call_seller_name = fields.Char(string='Kanban Last Call Seller Name', compute='_compute_kanban', store=1)
    kanban_last_call_phone = fields.Char(string='Kanban Last Call Phone', compute='_compute_kanban', store=1)
    kanban_activity_color = fields.Char(string='Kanban Activity Color', compute='_compute_activity_color')


    def _compute_activity_color(self):
        color = '#dedede'
        for record in self:
            if record.activity_ids:
                activity_model = record.activity_ids.search([('id', 'in', record.activity_ids.ids)], order='date_deadline asc',
                                                          limit=1)
                if activity_model:
                    date_deadline = activity_model.date_deadline
                    now_date = datetime.now().date()
                    if date_deadline < now_date:
                        color = '#bd2130'
                    elif date_deadline == now_date:
                        color = '#d39e00'
                    else:
                        color = '#1e7e34'

            record.kanban_activity_color = color

    @api.depends('call_ids')
    def _compute_kanban(self):
        for record in self:
            hotel_name = ''
            phone = ''
            try:
                if record.call_ids:
                    call_model = self.env['crm_voip.crm.customer.call'].browse(max(record.call_ids.ids))
                    hotel_name = call_model.seller_id.display_name
                    phone = call_model.phone
            except Exception as e:
                traceback.print_exc()

            record.kanban_last_call_seller_name = hotel_name
            record.kanban_last_call_phone = phone

    @api.model
    def default_get(self, fields):
        res = super(Customer, self).default_get(fields)
        if self.env.user.partner_id.parent_id:
            res['partner_id'] = self.env.user.partner_id.parent_id.id
        return res

    @api.model
    def create(self, vals):
        res = super(Customer, self).create(vals)
        if 'questions_ids' not in vals:
            questions = self.env['crm_voip.crm.questions'].search([('partner_id', '=', self.partner_id.id)])
            for q in questions:
                self.env['crm_voip.crm.customer.questions'].create({
                    'name': q.name,
                    'question_id': q.id,
                    'customer_id': res.id
                })
        return res


    def _search_fullname(self, operator, operand):
        if operand:
            name_part = operand.split(" ")
            where_part = []
            for n in name_part:
                where_part.append("(name ilike '%%%s%%' or surname ilike '%%%s%%')" % (n, n))
            query = "select id from crm_voip_crm_customer where %s limit 1000" % " and ".join(where_part)
            self.env.cr.execute(query)
            customer_ids = [customer['id'] for customer in self.env.cr.dictfetchall()]
            return [('id', 'in', customer_ids)]
        return [('id', '=', 0)]

    def _compute_full_name(self):
        for record in self:
            name_part = []
            if record.name:
                name_part.append(record.name)
            if record.surname:
                name_part.append(record.surname)
            record.full_name = " ".join(name_part)

    def _show_detail(self):
        for record in self:
            if record.sex == '1':
                record.sex_html = "<i class='fa fa-male' aria-hidden='true' style='font-size:14px;color:blue;font-weight:bold;' ></i>"
            elif record.sex == '2':
                record.sex_html = "<i class='fa fa-female' aria-hidden='true' style='font-size:14px;color:#fe4a49;font-weight:bold;' ></i>"
            else:
                record.sex_html = ''

    def unlink(self):
        odoobot_id = self.env['ir.model.data'].xmlid_to_res_id("base.partner_root")
        if self.env.user.id not in [SUPERUSER_ID, odoobot_id]:
            raise ValidationError(_('This Record Can Not Be Deleted!'))
        return super(Customer, self).unlink()


class CustomerSource(models.Model):
    _name = 'crm_voip.crm.customer.source'
    _rec_name = 'name'
    _description = 'Customer Source'

    partner_id = fields.Many2one(comodel_name='res.partner', string='Operator', domain=[('is_company', '=', True)],
                                 required=True)
    name = fields.Char("Name")

    @api.model
    def default_get(self, fields):
        res = super(CustomerSource, self).default_get(fields)
        if self.env.user.partner_id.parent_id:
            res['partner_id'] = self.env.user.partner_id.parent_id.id
        return res


class CustomerCall(models.Model):
    _name = 'crm_voip.crm.customer.call'
    _rec_name = 'phone'
    _description = 'CRM Customer Call'
    _order = "start desc"

    partner_id = fields.Many2one(comodel_name='res.partner', string='Operator', domain=[('is_company', '=', True)],
                                 required=True, index=True)
    user_id = fields.Many2one(comodel_name='res.users', compute='_compute_user_id', store=True)
    customer_id = fields.Many2one(comodel_name="crm_voip.crm.customer", string="Customer", index=True)
    customer_name = fields.Char('Name', related='customer_id.name')
    customer_surname = fields.Char('Surname', related='customer_id.surname')
    customer_full_name = fields.Char("Fullname", related='customer_id.full_name')
    phone_id = fields.Many2one(comodel_name="crm_voip.crm.customer.phone", string="Phone", index=True)
    seller_id = fields.Many2one('crm_voip.seller', string='Seller', index=True)
    unique_id = fields.Char("Unique ID")
    type = fields.Selection(string="Call Type", selection=[('inbound', 'Inbound'), ('outbound', 'Outbound')])
    phone = fields.Char("Phone")
    incoming_phone = fields.Char("Incoming Phone")
    start = fields.Datetime("Date")
    duration = fields.Integer("Duration")
    duration_show = fields.Char("Duration", compute='_compute_duration_show')
    call_icon = fields.Binary("Call Icon", compute='_compute_call_icon')
    unanswered = fields.Boolean("Unanswered", default=False)
    unanswered_first = fields.Boolean("Unanswered First", default=False)
    internal_number = fields.Char("Internal Number")
    call_record_source = fields.Char("Call Record Source")
    call_record = fields.Char("Call Record")
    call_play = fields.Char("Call Record", compute='_compute_call_play')
    log_ids = fields.One2many(comodel_name="crm_voip.crm.customer.call_log", inverse_name="call_id", string="Logs")
    update_phone = fields.Boolean("Update Phone", default=False)
    active = fields.Boolean(string='Active', default=True)
    call_end = fields.Boolean(string='Call End', default=False)
    record_url = fields.Char("Record Url")
    internal_user_contact = fields.Many2one('res.partner', string="Internal Number Contact")

    def call_record_listen(self):
        provider = self.env['crm_voip.providers.pbx'].search([])
        headers = {
            "Connection": "keep-alive",
            "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.5 (KHTML, like Gecko) Chrome/19.0.1084.52 Safari/536.5",
            "Content-Type": "application/json"
            }
        myobj = {
            "usercode": provider.username,
            "password": provider.password,
            "uniqueid": self.unique_id
        }
        x = requests.post("https://api.netgsm.com.tr/netsantral/report", json = myobj, headers=headers)
        last_result = json.loads((x.content))
        if len(json.loads((x.content))[0]['values'][0]['recording']) > 0:
            last_result = str(json.loads((x.content))[0]['values'][0]['recording'])
            company = self.env['res.company'].sudo().search([('id','=', 1)])
            company.write({
                'social_twitter' : last_result
                })
        return { 'name': 'Go to website',
                'res_model': 'ir.actions.act_url',
                'type': 'ir.actions.act_url',
                'target' : 'self',
                'url': "https://artin.nitrawork.com/listen-voice?" + (last_result[last_result.index('y='):len(last_result)])
        }



    def write(self, vals):
        if 'active' in vals and not self.user_has_groups(
                'crm_voip.crm_voip_full_access,crm_voip.crm_voip_operator_manager_group'):
            del vals['active']
            if len(vals) == 0:
                raise ValidationError(_('This operation can only be done by the authorities'))
        result = super(CustomerCall, self).write(vals)
        print(vals)
        if 'customer_id' in vals and 'update_phone' not in vals:
            for call_record in self:
                call_record.phone_id.write({
                    'customer_id': vals['customer_id']
                })
        return result

    @api.model
    def default_get(self, fields):
        res = super(CustomerCall, self).default_get(fields)
        if self.env.user.partner_id.parent_id:
            res['partner_id'] = self.env.user.partner_id.parent_id.id
        return res

    @api.model
    def create(self, vals):
        if 'unique_id' in vals:
            call_record = self.env['crm_voip.crm.customer.call'].search([('unique_id', '=', vals['unique_id'])])
            if call_record:
                write_val = {}
                for key, value in vals.items():
                    if value:
                        write_val[key] = value
                call_record.write(vals)
                return call_record
        return super(CustomerCall, self).create(vals)

    def mark_answered(self):
        for record in self:
            record.unanswered = False
            record.env['bus.bus'].sendone("unanswered", "change")

    @api.depends('internal_number')
    def _compute_user_id(self):
        for record in self:
            record.user_id = False
            partner_env = self.env['res.partner'].sudo()
            partner_model = partner_env.search([('phone', '=', record.internal_number)])
            if partner_model and record.internal_number:
                user_env = self.env['res.users'].sudo()
                user_model = user_env.search(
                    [('partner_id', 'in', partner_model.ids), ('partner_id.parent_id', '=', record.partner_id.id)], limit=1)
                if user_model:
                    record.user_id = user_model.id

    def _compute_call_play(self):
        for record in self:
            if record.call_record:
                record.call_play = record.call_record.replace('/var/', '/')
            else:
                record.call_play = ''

    def call_phone(self):
        call_wizard_record = self.env['crm_voip.crm.call_wizard'].create({
            'phone_id': self.phone_id.id,
            'seller_id': self.seller_id.id,
            'call_id': self.id,
        })
        self.unanswered = False
        self.env['bus.bus'].sendone("unanswered", "change")
        return {
            'type': 'ir.actions.act_window',
            'name': 'Call Wizard',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'crm_voip.crm.call_wizard',
            'res_id': call_wizard_record.id,
            'target': 'new',
        }


    def send_sms_wizard(self):
        sms_record = self.env['crm_voip.crm.customer.sms_wizard'].create({
            'phone_id': self.phone_id.id,
        })
        return {
            'type': 'ir.actions.act_window',
            'name': 'Send SMS',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'crm_voip.crm.customer.sms_wizard',
            'res_id': sms_record.id,
            'target': 'new',
        }

    def _compute_call_icon(self):
        for record in self:
            if record.type == 'inbound':
                record.call_icon = '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'
            else:
                record.call_icon = 'iVBORw0KGgoAAAANSUhEUgAAABgAAAAYCAYAAADgdz34AAAACXBIWXMAAAsTAAALEwEAmpwYAAAKT2lDQ1BQaG90b3Nob3AgSUNDIHByb2ZpbGUAAHjanVNnVFPpFj333vRCS4iAlEtvUhUIIFJCi4AUkSYqIQkQSoghodkVUcERRUUEG8igiAOOjoCMFVEsDIoK2AfkIaKOg6OIisr74Xuja9a89+bN/rXXPues852zzwfACAyWSDNRNYAMqUIeEeCDx8TG4eQuQIEKJHAAEAizZCFz/SMBAPh+PDwrIsAHvgABeNMLCADATZvAMByH/w/qQplcAYCEAcB0kThLCIAUAEB6jkKmAEBGAYCdmCZTAKAEAGDLY2LjAFAtAGAnf+bTAICd+Jl7AQBblCEVAaCRACATZYhEAGg7AKzPVopFAFgwABRmS8Q5ANgtADBJV2ZIALC3AMDOEAuyAAgMADBRiIUpAAR7AGDIIyN4AISZABRG8lc88SuuEOcqAAB4mbI8uSQ5RYFbCC1xB1dXLh4ozkkXKxQ2YQJhmkAuwnmZGTKBNA/g88wAAKCRFRHgg/P9eM4Ors7ONo62Dl8t6r8G/yJiYuP+5c+rcEAAAOF0ftH+LC+zGoA7BoBt/qIl7gRoXgugdfeLZrIPQLUAoOnaV/Nw+H48PEWhkLnZ2eXk5NhKxEJbYcpXff5nwl/AV/1s+X48/Pf14L7iJIEyXYFHBPjgwsz0TKUcz5IJhGLc5o9H/LcL//wd0yLESWK5WCoU41EScY5EmozzMqUiiUKSKcUl0v9k4t8s+wM+3zUAsGo+AXuRLahdYwP2SycQWHTA4vcAAPK7b8HUKAgDgGiD4c93/+8//UegJQCAZkmScQAAXkQkLlTKsz/HCAAARKCBKrBBG/TBGCzABhzBBdzBC/xgNoRCJMTCQhBCCmSAHHJgKayCQiiGzbAdKmAv1EAdNMBRaIaTcA4uwlW4Dj1wD/phCJ7BKLyBCQRByAgTYSHaiAFiilgjjggXmYX4IcFIBBKLJCDJiBRRIkuRNUgxUopUIFVIHfI9cgI5h1xGupE7yAAygvyGvEcxlIGyUT3UDLVDuag3GoRGogvQZHQxmo8WoJvQcrQaPYw2oefQq2gP2o8+Q8cwwOgYBzPEbDAuxsNCsTgsCZNjy7EirAyrxhqwVqwDu4n1Y8+xdwQSgUXACTYEd0IgYR5BSFhMWE7YSKggHCQ0EdoJNwkDhFHCJyKTqEu0JroR+cQYYjIxh1hILCPWEo8TLxB7iEPENyQSiUMyJ7mQAkmxpFTSEtJG0m5SI+ksqZs0SBojk8naZGuyBzmULCAryIXkneTD5DPkG+Qh8lsKnWJAcaT4U+IoUspqShnlEOU05QZlmDJBVaOaUt2ooVQRNY9aQq2htlKvUYeoEzR1mjnNgxZJS6WtopXTGmgXaPdpr+h0uhHdlR5Ol9BX0svpR+iX6AP0dwwNhhWDx4hnKBmbGAcYZxl3GK+YTKYZ04sZx1QwNzHrmOeZD5lvVVgqtip8FZHKCpVKlSaVGyovVKmqpqreqgtV81XLVI+pXlN9rkZVM1PjqQnUlqtVqp1Q61MbU2epO6iHqmeob1Q/pH5Z/YkGWcNMw09DpFGgsV/jvMYgC2MZs3gsIWsNq4Z1gTXEJrHN2Xx2KruY/R27iz2qqaE5QzNKM1ezUvOUZj8H45hx+Jx0TgnnKKeX836K3hTvKeIpG6Y0TLkxZVxrqpaXllirSKtRq0frvTau7aedpr1Fu1n7gQ5Bx0onXCdHZ4/OBZ3nU9lT3acKpxZNPTr1ri6qa6UbobtEd79up+6Ynr5egJ5Mb6feeb3n+hx9L/1U/W36p/VHDFgGswwkBtsMzhg8xTVxbzwdL8fb8VFDXcNAQ6VhlWGX4YSRudE8o9VGjUYPjGnGXOMk423GbcajJgYmISZLTepN7ppSTbmmKaY7TDtMx83MzaLN1pk1mz0x1zLnm+eb15vft2BaeFostqi2uGVJsuRaplnutrxuhVo5WaVYVVpds0atna0l1rutu6cRp7lOk06rntZnw7Dxtsm2qbcZsOXYBtuutm22fWFnYhdnt8Wuw+6TvZN9un2N/T0HDYfZDqsdWh1+c7RyFDpWOt6azpzuP33F9JbpL2dYzxDP2DPjthPLKcRpnVOb00dnF2e5c4PziIuJS4LLLpc+Lpsbxt3IveRKdPVxXeF60vWdm7Obwu2o26/uNu5p7ofcn8w0nymeWTNz0MPIQ+BR5dE/C5+VMGvfrH5PQ0+BZ7XnIy9jL5FXrdewt6V3qvdh7xc+9j5yn+M+4zw33jLeWV/MN8C3yLfLT8Nvnl+F30N/I/9k/3r/0QCngCUBZwOJgUGBWwL7+Hp8Ib+OPzrbZfay2e1BjKC5QRVBj4KtguXBrSFoyOyQrSH355jOkc5pDoVQfujW0Adh5mGLw34MJ4WHhVeGP45wiFga0TGXNXfR3ENz30T6RJZE3ptnMU85ry1KNSo+qi5qPNo3ujS6P8YuZlnM1VidWElsSxw5LiquNm5svt/87fOH4p3iC+N7F5gvyF1weaHOwvSFpxapLhIsOpZATIhOOJTwQRAqqBaMJfITdyWOCnnCHcJnIi/RNtGI2ENcKh5O8kgqTXqS7JG8NXkkxTOlLOW5hCepkLxMDUzdmzqeFpp2IG0yPTq9MYOSkZBxQqohTZO2Z+pn5mZ2y6xlhbL+xW6Lty8elQfJa7OQrAVZLQq2QqboVFoo1yoHsmdlV2a/zYnKOZarnivN7cyzytuQN5zvn//tEsIS4ZK2pYZLVy0dWOa9rGo5sjxxedsK4xUFK4ZWBqw8uIq2Km3VT6vtV5eufr0mek1rgV7ByoLBtQFr6wtVCuWFfevc1+1dT1gvWd+1YfqGnRs+FYmKrhTbF5cVf9go3HjlG4dvyr+Z3JS0qavEuWTPZtJm6ebeLZ5bDpaql+aXDm4N2dq0Dd9WtO319kXbL5fNKNu7g7ZDuaO/PLi8ZafJzs07P1SkVPRU+lQ27tLdtWHX+G7R7ht7vPY07NXbW7z3/T7JvttVAVVN1WbVZftJ+7P3P66Jqun4lvttXa1ObXHtxwPSA/0HIw6217nU1R3SPVRSj9Yr60cOxx++/p3vdy0NNg1VjZzG4iNwRHnk6fcJ3/ceDTradox7rOEH0x92HWcdL2pCmvKaRptTmvtbYlu6T8w+0dbq3nr8R9sfD5w0PFl5SvNUyWna6YLTk2fyz4ydlZ19fi753GDborZ752PO32oPb++6EHTh0kX/i+c7vDvOXPK4dPKy2+UTV7hXmq86X23qdOo8/pPTT8e7nLuarrlca7nuer21e2b36RueN87d9L158Rb/1tWeOT3dvfN6b/fF9/XfFt1+cif9zsu72Xcn7q28T7xf9EDtQdlD3YfVP1v+3Njv3H9qwHeg89HcR/cGhYPP/pH1jw9DBY+Zj8uGDYbrnjg+OTniP3L96fynQ89kzyaeF/6i/suuFxYvfvjV69fO0ZjRoZfyl5O/bXyl/erA6xmv28bCxh6+yXgzMV70VvvtwXfcdx3vo98PT+R8IH8o/2j5sfVT0Kf7kxmTk/8EA5jz/GMzLdsAAAAgY0hSTQAAeiUAAICDAAD5/wAAgOkAAHUwAADqYAAAOpgAABdvkl/FRgAAA9ZJREFUeNq0VV1oHFUU/s6dn92ZbGZ3Y7dbq21CbZq2VIsPbVWwRFErFZE+Ku2DICq1L76KL6IvVlEMihQpitKgSChFEOmDLYgWY1qU1CitLWnS5meb3c3uzuzu7My9x4ds4iYZTAJ64cDMcOZ89zvf+e4lZsb/ufSoj5dzJ1veCIJ0BLKCK/kvdnuNmwfuTDzc58R76ilrG5jlsv93Zo4sPIuV9zDHMJCVtOtP9vmh+3bJHz0mSIMgDURi7QzqYa25d0JDuijUho1pd/DLeljZT2Qi5428Ezc2Niw92wcS0MhcGwCzAoEghAFmiYnK0EAtKDwhKNYkZGG0eP6DQvXGzKbko/0dVg8AWj1AqEJIDlCrj2HK/eWE6xeeFiIGuWgeBIr18c+T8Ztexr7vjIIEWK0WgNGQNVzNn33PC6Ze1CgOqaLUEdpo8cf+Wug9nrHv/anNzC7LiVTIVy4mKhdfrzQKrwIWJIvIUKwjYLbHS0PfztbH9wACasnYRzK4nv/hlZz3x5v6srZEsSAoRnKsNHTaMrL7Dc26vrLI0GaJ7A9DVp4gbR8z90aXJxnXnc8ALisOrav5cw6RhgP3vPHvALax7hTj2ikiE0TWy4Gs9s77oXXS2sz0SFf6gRdulS+BoaCRDl4idKQGCgEs4w7c1f4QHLOzHCrCXIhFEUgaznvTENQ+Vzji2IlkQNDRpm2FkgLg2O9SGghVAGqZdYaABjl9250EAMRNE4aBZSCRAEHggKAQSIZOzrBtrP+z4E1ubzUTs4JJhpTQwWC4NaDqh8sMF+0DaSykCRJKR+J7ILbdDxoQRE0Agk+q3dTsBYMpuUonp+wNc0UUQzGQIet4NXSf8+q51D8MCLoQ3QYloKAABoQhYJjayiJ7ecCdYbBvocPZgGz7lhtpc8v7SduBV1Oo+0C9QahU/R0yNNpYxqAbbZi9JfHzwOhiPaMunJSTACuGGTdx6PmDeObwkzCTunbhr9NfF6uTh8ZyxWarFPZ2PbZvnZMdvD05g+MvnUR+qozWmpEMShUPZa+KmfwsPnm3H0ceOYaBj76TYSn9bCKR+Wbrpo1QSkexEqDoVp66u6MHF89eQ36qDG3pREYx0ImW+GLOZu0pC90PdmnbejNHO3cn3iq4rjM+UfZ2bt6z9/ynF0YunbkMDUDYUnMlAK05CAKAUAAxwATy1nendt1/sPNoaod92EyZ8sq54muDJ377GADkGgA6ACQBGE2w+Q4ICdQB1GK2nkltTuzSLN3K/Zr/SjGXZEvR1TDQ5hk0XUSLjiQgVECjmSwAyBVb9F+uvwcAH5XhN/cFBPEAAAAASUVORK5CYII='

    def _compute_duration_show(self):
        for record in self:
            record.duration_show = time.strftime('%H:%M:%S', time.gmtime(record.duration))

    def unlink(self):
        odoobot_id = self.env['ir.model.data'].xmlid_to_res_id("base.partner_root")
        if self.env.user.id not in [SUPERUSER_ID, odoobot_id]:
            raise ValidationError(_('This Record Can Not Be Deleted!'))
        return super(CustomerCall, self).unlink()


class CustomerPhone(models.Model):
    _name = 'crm_voip.crm.customer.phone'
    _rec_name = 'phone'
    _description = 'CRM Customer Phone'
    _order = "id desc"

    partner_id = fields.Many2one(comodel_name='res.partner', string='Operator', domain=[('is_company', '=', True)],
                                 required=True, index=True)
    customer_id = fields.Many2one(comodel_name="crm_voip.crm.customer", string="Customer", index=True)
    full_name = fields.Char("Fullname", related='customer_id.full_name')
    name = fields.Char("Name", related='customer_id.name')
    surname = fields.Char("Surname", related='customer_id.surname')
    note = fields.Char("Note", related='customer_id.note')

    phone = fields.Char("Phone", index=True)
    phone_type = fields.Selection(string="Phone Type",
                                  selection=[('mobile', 'Mobile'), ('work', 'Work'), ('home', 'Home'),
                                             ('public', 'Public')])
    call_ids = fields.One2many(comodel_name="crm_voip.crm.customer.call", inverse_name="phone_id", string="Calls")
    description = fields.Char("Description")

    @api.model
    def default_get(self, fields):
        res = super(CustomerPhone, self).default_get(fields)
        if self.env.user.partner_id.parent_id:
            res['partner_id'] = self.env.user.partner_id.parent_id.id
        return res


    def call_phone(self):
        call_search = self.env['crm_voip.crm.customer.call'].search([('phone_id', '=', self.id)], limit=1,
                                                                   order='id desc')
        call_wizard_record = self.env['crm_voip.crm.call_wizard'].create({
            'phone_id': self.id,
            'seller_id': call_search.seller_id.id if call_search else False
        })
        return {
            'type': 'ir.actions.act_window',
            'name': 'Call Wizard',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'crm_voip.crm.call_wizard',
            'res_id': call_wizard_record.id,
            'target': 'new',
        }

    _sql_constraints = [
        ("crm_voip_unique_crm_phone",
         "UNIQUE(partner_id, phone)",
         "Phone number already exist"),
    ]


    def send_sms_wizard(self):
        sms_record = self.env['crm_voip.crm.customer.sms_wizard'].create({
            'phone_id': self.id
        })
        return {
            'type': 'ir.actions.act_window',
            'name': 'Send SMS',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'crm_voip.crm.customer.sms_wizard',
            'res_id': sms_record.id,
            'target': 'new',
        }


    def open_wizard(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Create Customer',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'crm_voip.crm.create_customer_wizard',
            # 'res_id': search.id,
            'context': {'call_id': self.call_ids[0].id},
            'target': 'new',
        }

    def write(self, vals):
        result = super(CustomerPhone, self).write(vals)
        if 'customer_id' in vals:
            for phone in self:
                for c in phone.call_ids:
                    c.write({
                        'customer_id': vals['customer_id'],
                        'update_phone': not c.update_phone,
                    })
        return result

    def unlink(self):
        odoobot_id = self.env['ir.model.data'].xmlid_to_res_id("base.partner_root")
        if self.env.user.id not in [SUPERUSER_ID, odoobot_id]:
            raise ValidationError(_('This Record Can Not Be Deleted!'))
        return super(CustomerPhone, self).unlink()
