# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import Warning


class CrmCreateCustomer(models.TransientModel):
    _name = 'crm_voip.crm.create_customer_wizard'
    _description = "Customer Wizard"

    customer_id = fields.Many2one(comodel_name="crm_voip.crm.customer", string="Customer")
    call_id = fields.Many2one(comodel_name="crm_voip.crm.customer.call", string="Phone")
    new_customer = fields.Boolean("New Customer", default=False)
    same_customer_id = fields.Many2one(comodel_name="crm_voip.crm.customer", string="Same Customer")
    same_customer_exist = fields.Boolean("Same Customer Exist")
    name = fields.Char("Name")
    surname = fields.Char("Surname")

    sex = fields.Selection([('1', 'Male'), ('2', 'Female')], "Sex")
    nationality = fields.Selection([('1', 'TC'), ('2', 'Other')], "Nationality")
    note = fields.Char("Note")

    existing_name = fields.Char("Name", related="customer_id.name")
    existing_surname = fields.Char("Surname", related="customer_id.surname")
    existing_sex = fields.Selection(string="Sex", related="customer_id.sex")
    existing_nationality = fields.Selection(string="Nationality", related="customer_id.nationality")
    existing_note = fields.Char("Note", related="customer_id.note")
    questions_ids = fields.One2many(comodel_name="crm_voip.crm.create_customer_wizard.questions",
                                    inverse_name="wizard_id", string="Questions")
    black_list = fields.Boolean("Black List", default=False)
    permit_communication = fields.Boolean("Permit Communication", default=False)


    def select_same_customer(self):
        self.ensure_one()
        if not self.same_customer_exist:
            raise Warning(_("Please select a same user"))
        self.customer_id = self.same_customer_id.id
        self.new_customer = False
        return {
            'context': self.env.context,
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'crm_voip.crm.create_customer_wizard',
            'res_id': self.id,
            'view_id': False,
            'type': 'ir.actions.act_window',
            'target': 'new',
        }

    @api.onchange('name', 'surname')
    def _onchange_for_same_user(self):
        customer = self.env['crm_voip.crm.customer'].search([('name', '=ilike', self.name),
                                                            ('surname', '=ilike', self.surname)],
                                                           order='id desc', limit=1)
        if customer:
            self.same_customer_exist = True
            self.same_customer_id = customer.id
        else:
            self.same_customer_exist = False
            self.same_customer_id = False


    @api.model
    def default_get(self, fields):
        res = super(CrmCreateCustomer, self).default_get(fields)
        if 'call_id' not in self._context:
            raise Warning(_("Call Not Found"))
        res['call_id'] = self._context['call_id']
        questions = self.env['crm_voip.crm.questions'].search([])
        questions_ids = []
        for q in questions:
            questions_ids.append((0, 0, {
                'name': q.name,
                'question_id': q.id
            }))
        if questions_ids:
            res['questions_ids'] = questions_ids
        return res

    @api.onchange("new_customer")
    def _onchange_new_customer(self):
        if self.new_customer and self.customer_id:
            self.customer_id = False


    def open_customer(self):
        self.ensure_one()
        self.call_id.phone_id.write({
            'customer_id': self.customer_id.id,
        })
        return {
            'type': 'ir.actions.act_window',
            'name': 'Customer',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'crm_voip.crm.customer',
            # 'context': {'form_view_initial_mode': 'edit', 'force_detailed_view': 'true'},
            'res_id': self.customer_id.id,
            'target': 'current',
            'flags': {'form': {'action_buttons': True, 'options': {'clear_breadcrumbs': True}}}
        }

    def create_and_open(self):
        self.ensure_one()
        questions_ids = []
        for q in self.questions_ids:
            questions_ids.append((0, 0, {
                'name': q.name,
                'answer': q.answer,
                'answer_id': q.answer_id.id,
                'question_id': q.question_id.id
            }))
        customer = self.env['crm_voip.crm.customer'].create({
            'partner_id': self.call_id.partner_id.id,
            'name': self.name,
            'surname': self.surname,
            'sex': self.sex,
            'nationality': self.nationality,
            'note': self.note,
            'black_list': self.black_list,
            'permit_communication': self.permit_communication,
            'questions_ids': questions_ids,
        })
        self.call_id.phone_id.write({
            'customer_id': customer.id,
        })
        return {
            'type': 'ir.actions.act_window',
            'name': 'Customer',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'crm_voip.crm.customer',
            # 'context': {'form_view_initial_mode': 'edit', 'force_detailed_view': 'true'},
            'res_id': customer.id,
            'target': 'current',
            'flags': {'form': {'action_buttons': True, 'options': {'clear_breadcrumbs': True}}}
        }


class CustomerWizardQuestion(models.TransientModel):
    _name = 'crm_voip.crm.create_customer_wizard.questions'
    _rec_name = 'name'
    _description = 'Customer Question'

    name = fields.Char("Question")
    answer = fields.Char("Answer")

    question_id = fields.Many2one(comodel_name="crm_voip.crm.questions", string="Question", required=False)
    wizard_id = fields.Many2one(comodel_name="crm_voip.crm.create_customer_wizard", string="Wizard", required=False)
    answer_id = fields.Many2one(comodel_name="crm_voip.crm.answer", string="Ready Answer", required=False)

    @api.onchange('answer_id')
    def _onchange_answer(self):
        self.answer = self.answer_id.name
