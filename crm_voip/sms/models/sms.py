# -*- coding: utf-8 -*-
import base64
import json
import sys

import re
import urllib

from odoo import api
from odoo import exceptions
from odoo import fields
from odoo import models
from ...library.two_way_encryption import encrypt_text, dencrypt_text


class SmsServices(models.Model):
    _name = 'crm_voip.providers.sms_services'
    _description = 'Sms Provider'
    name = fields.Char('Name', required=True)
    request_type = fields.Selection([('post', 'POST'), ('get', 'GET')], 'Request Type')
    service_url = fields.Char('Service Url')
    parameters = fields.One2many('crm_voip.providers.sms_services.parameters', 'service_id')
    http_headers = fields.One2many('crm_voip.providers.sms_services.http_header', 'service_id')
    partner_ids = fields.One2many('res.partner', inverse_name='sms_provider', string='Operator')
    match_type = fields.Selection([('on_success', 'On Success'), ('on_failure', 'On Failure')], 'Regex Match Type',
                                  require=True)
    match_regex = fields.Text('Regex')
    default = fields.Boolean("Default")


    def test(self):
        user = self.env['res.partner'].browse(7)
        sms_content = user.sms_content % '123456'
        self.send_sms_by_user(user, '5426891425', sms_content)

    def send_sms_by_user(self, partner_model, mobile_number, sms_content):
        sms_provider = self.search([('partner_ids', 'in', partner_model.id)])
        sms_log_param = {
            'partner_id': partner_model.id,
            'mobile_number': mobile_number,
            'sms_content': sms_content
        }

        if sms_provider:
            import requests
            sms_log_param['service_id'] = sms_provider.id

            url = sms_provider.service_url
            params = {}
            parameters = sms_provider.parameters.read(['param_name', 'param_dynamic_value', 'param_static_value'],
                                                      '_classic_read')
            for parameter in parameters:
                if parameter['param_dynamic_value'] == 'static':
                    params[parameter['param_name']] = parameter['param_static_value']
                elif parameter['param_dynamic_value'] == 'content':
                    params[parameter['param_name']] = sms_content
                elif parameter['param_dynamic_value'] == 'number':
                    params[parameter['param_name']] = mobile_number
                elif parameter['param_dynamic_value'] == 'content_b64':
                    params[parameter['param_name']] = base64.b64encode(sms_content.encode('utf-8'))
                elif parameter['param_dynamic_value'] == 'number_list':
                    params[parameter['param_name']] = [mobile_number]

            headers = {}
            parameters = sms_provider.http_headers.read(['param_name', 'param_static_value'],
                                                        '_classic_read')
            for parameter in parameters:
                headers[parameter['param_name']] = parameter['param_static_value']

            result = ""
            if sms_provider.request_type == 'post':
                result = requests.post(url, data=json.dumps(params), headers=headers).text
            elif sms_provider.request_type == 'get':
                result = requests.get(url, params=params, headers=headers).text

            p = re.compile(sms_provider.match_regex)
            is_match = p.match(result)
            sms_log_param['result_text'] = result

            operation_result = ""
            is_matched = False

            if is_match:
                if sms_provider.match_type == 'on_success':
                    operation_result = True
                if sms_provider.match_type == 'on_failure':
                    operation_result = False
                is_matched = True
            else:
                if sms_provider.match_type == 'on_success':
                    operation_result = False
                if sms_provider.match_type == 'on_failure':
                    operation_result = True
            sms_log_param['result'] = result
            self.env['crm_voip.sms.log'].sudo().create(sms_log_param)
            return operation_result
        else:
            sms_log_param.update({
                'result': False,
                'result_text': 'Sms Service Not Found'
            })
            self.env['crm_voip.sms.log'].sudo().create(sms_log_param)
            return False


class SmsServicesParameters(models.Model):
    _name = 'crm_voip.providers.sms_services.parameters'
    _description = 'Sms Provider Parameters'
    _order = 'sequence ASC'

    service_id = fields.Many2one('crm_voip.providers.sms_services', 'Service')
    param_name = fields.Text('Param Name', require=True)
    param_dynamic_value = fields.Selection(
        [('static', 'Static Value'), ('content', 'Sms Content'), ('content_b64', 'Sms Content (Base64)'),
         ('number', 'User Phone'), ('number_list', 'User Phone (List)')], 'Param Dynamic Value')
    param_static_value = fields.Text('Param Static Value')
    sequence = fields.Integer('Sequence', default=0)


    def read(self, fields=None, load='_classic_read'):
        self.check_access_rule('read')
        super_read = super(SmsServicesParameters, self).read(fields=fields, load=load)
        if load == '_classic_read':
            for row in super_read:
                for key, value in row.items():
                    if key in ['param_name', 'param_static_value', 'param_value'] and row[key]:
                        row[key] = dencrypt_text(value)
        return super_read


    def write(self, vals):
        for key, value in vals.items():
            if key in ['param_name', 'param_static_value', 'param_value'] and vals[key]:
                vals[key] = encrypt_text(value)
        return super(SmsServicesParameters, self).write(vals)

    @api.model
    def create(self, vals):
        for key, value in vals.items():
            if key in ['param_name', 'param_static_value', 'param_value'] and vals[key]:
                vals[key] = encrypt_text(value)
        return super(SmsServicesParameters, self).create(vals)


class SmsServicesHttpHeader(models.Model):
    _name = 'crm_voip.providers.sms_services.http_header'
    _description = 'Sms Provider Http Headers'
    _order = 'sequence ASC'

    service_id = fields.Many2one('crm_voip.providers.sms_services', 'Service')
    param_name = fields.Text('Param Name', require=True)
    param_static_value = fields.Text('Param Value')
    sequence = fields.Integer('Sequence', default=0)


    def read(self, fields=None, load='_classic_read'):
        self.check_access_rule('read')
        super_read = super(SmsServicesHttpHeader, self).read(fields=fields, load=load)
        if load == '_classic_read':
            for row in super_read:
                for key, value in row.items():
                    if key in ['param_name', 'param_static_value'] and row[key]:
                        row[key] = dencrypt_text(value)
        return super_read


    def write(self, vals):
        for key, value in vals.items():
            if key in ['param_name', 'param_static_value'] and vals[key]:
                vals[key] = encrypt_text(value)
        return super(SmsServicesHttpHeader, self).write(vals)

    @api.model
    def create(self, vals):
        for key, value in vals.items():
            if key in ['param_name', 'param_static_value'] and vals[key]:
                vals[key] = encrypt_text(value)
        return super(SmsServicesHttpHeader, self).create(vals)


class SmsServicesTestWizard(models.TransientModel):
    _name = "crm_voip.providers.sms_services.test"
    _description = 'Sms Provider Test Wizard'

    def _default_service_name(self):
        service_id = self._context.get('active_ids') or []
        return self.env['crm_voip.providers.sms_services'].browse(service_id).name

    service_name = fields.Char('Service Name', default=_default_service_name, readonly=True)
    test_gsm = fields.Char('Gsm Number')


    def test_configuration(self):

        import requests
        sms_provider = self.env['crm_voip.providers.sms_services'].browse(self.env.context['active_ids'])
        url = sms_provider.service_url
        params = {}
        parameters = sms_provider.parameters.read(['param_name', 'param_dynamic_value', 'param_static_value'],
                                                  '_classic_read')
        for parameter in parameters:
            if parameter['param_dynamic_value'] == 'static':
                params[parameter['param_name']] = parameter['param_static_value']
            elif parameter['param_dynamic_value'] == 'content':
                params[parameter['param_name']] = "This is test message. TR Test: ığüşiöçĞÜŞİÖÇ"
            elif parameter['param_dynamic_value'] == 'content_b64':
                params[parameter['param_name']] = base64.b64encode("b'This is test message. TR Test: ığüşiöçĞÜŞİÖÇ".encode("utf-8"))
            elif parameter['param_dynamic_value'] == 'number':
                params[parameter['param_name']] = self.test_gsm
            elif parameter['param_dynamic_value'] == 'number_list':
                params[parameter['param_name']] = [self.test_gsm]

        headers = {}
        parameters = sms_provider.http_headers.read(['param_name', 'param_static_value'],
                                                    '_classic_read')
        for parameter in parameters:
            headers[parameter['param_name']] = parameter['param_static_value']

        result = ""
        if sms_provider.request_type == 'post':
            result = requests.post(url, data=json.dumps(params), headers=headers).text
        elif sms_provider.request_type == 'get':
            result = requests.get(url, params=params, headers=headers).text

        p = re.compile(sms_provider.match_regex)
        is_match = p.match(result)

        operation_result = ""
        is_matched = False
        if is_match:
            if sms_provider.match_type == 'on_success':
                operation_result = "Send Successfull"
            if sms_provider.match_type == 'on_failure':
                operation_result = "Send Failure"
            is_matched = True
        else:
            if sms_provider.match_type == 'on_success':
                operation_result = "Send Failure"
            if sms_provider.match_type == 'on_failure':
                operation_result = "Send Successfull"

        raise exceptions.Warning(
            'Provider Result: %s \n Regex Match: %s \n Operation Result: %s' % (result, is_matched, operation_result))
