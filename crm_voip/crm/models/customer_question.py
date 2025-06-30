# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
import time


class Answer(models.Model):
    _name = 'crm_voip.crm.answer'
    _rec_name = 'name'
    _description = 'Answer'

    name = fields.Char("Answer")
    question_id = fields.Many2one(comodel_name="crm_voip.crm.questions", string="Question", required=False)


class Question(models.Model):
    _name = 'crm_voip.crm.questions'
    _rec_name = 'name'
    _description = 'Question'
    _order = 'sequence ASC'

    partner_id = fields.Many2one(comodel_name='res.partner', string='Operator', domain=[('is_company', '=', True)],
                                 required=True)
    name = fields.Char("Question")
    answer_ids = fields.One2many(comodel_name="crm_voip.crm.answer", inverse_name="question_id", string="Answers")
    sequence = fields.Integer('Sequence', default=100)

    @api.model
    def default_get(self, fields):
        res = super(Question, self).default_get(fields)
        if self.env.user.partner_id.parent_id:
            res['partner_id'] = self.env.user.partner_id.parent_id.id
        return res


class CustomerQuestion(models.Model):
    _name = 'crm_voip.crm.customer.questions'
    _rec_name = 'name'
    _description = 'Customer Question'

    name = fields.Char("Question")
    answer = fields.Char("Answer")

    question_id = fields.Many2one(comodel_name="crm_voip.crm.questions", string="Question", required=False)
    customer_id = fields.Many2one(comodel_name="crm_voip.crm.customer", string="Customer", required=False)
    answer_id = fields.Many2one(comodel_name="crm_voip.crm.answer", string="Ready Answer", required=False)

    @api.onchange('answer_id')
    def _onchange_answer(self):
        self.answer = self.answer_id.name
