# -*- coding: utf-8 -*-
from odoo import api, fields, models, tools
from odoo import http
from odoo.http import request, route
from datetime import datetime
import logging
import requests
import json
_logger = logging.getLogger(__name__)
from odoo.tools import date_utils
import uuid
import base64
from odoo.addons.portal.controllers.portal import CustomerPortal
import os

class seocheckerPortalController(CustomerPortal):
    @route(['/my/text'], type='http', auth='public', website=True, csrf=False)
    def get_text_analysis_form(self, redirect=None, **kw):
        attachment_ids_list = []
        unique_uuid = uuid.uuid4()
        partner_id = request.env.user.partner_id
        Attachment = request.env['ir.attachment']
        file = kw.get('attachment')
        attachment_id = Attachment.sudo().create({
            'name': file.filename,
            'type': 'binary',
            'datas': base64.encodebytes(file.read()),
            'res_model': "seochecker.profile",
            'public': True
        })
        attachment_ids_list.append(attachment_id.id)
        seochecker = http.request.env['seochecker.profile'].sudo().create({
                'name': kw.get('website_name_input'),
                'website': kw.get('website_name_input'),
                'user': request.env.user.id,
                'uuid': unique_uuid,
                'main_website': True
            })
        seochecker.write({
            'seo_text_file' : [(6, 0,attachment_ids_list)]
            })
        return request.redirect("/seo-results?token=" + str(unique_uuid))
    
    @route(['/my/text2'], type='http', auth='public', website=True, csrf=False)
    def get_text_analysis_form(self, redirect=None, **kw):
        attachment_ids_list = []
        unique_uuid = uuid.uuid4()
        partner_id = request.env.user.partner_id
        seochecker = http.request.env['seochecker.profile'].sudo().create({
                'title': kw.get('title'),
                'keywords': kw.get('keyword_1'),
                'content': kw.get('content'),
                'headings': kw.get('headings'),
                'number_of_images': kw.get('number_of_images'),
                'country_id': kw.get('country_input'),
                'user': request.env.user.id,
                'uuid': unique_uuid,
                'main_website': True
            })
        seochecker.google_api_web_search()
        seochecker.google_api_keyword()
        competitors = http.request.env['seochecker.profile'].sudo().search([["related_main_website.id","=",seochecker.id]])
        for competitor in competitors:
            competitor["country_id"] = seochecker.country_id.id
            competitor.seo_fast_extraction_api()
            competitor.seoanalyzer_analyze()
        return request.redirect("/seo-results?token=" + str(unique_uuid))
    
    @route(['/my/visual'], type='http', auth='public', website=True, csrf=False)
    def get_visual_analysis_form(self, redirect=None, **kw):
        attachment_ids_list = []
        unique_uuid = uuid.uuid4()
        partner_id = request.env.user.partner_id
        Attachment = request.env['ir.attachment']
        file = kw.get('attachment')
        attachment_id = Attachment.sudo().create({
            'name': file.filename,
            'type': 'binary',
            'datas': base64.encodebytes(file.read()),
            'res_model': "seochecker.profile",
            'public': True
        })
        attachment_ids_list.append(attachment_id.id)
        seochecker = http.request.env['seochecker.profile'].sudo().create({
                'name': kw.get('website_name_input'),
                'website': kw.get('website_name_input'),
                'user': request.env.user.id,
                'uuid': unique_uuid,
                'main_website': True
            })
        seochecker.write({
            'seo_visual_file' : [(6, 0,attachment_ids_list)]
            })
        return request.redirect("/seo-results?token=" + str(unique_uuid))

class seocheckerProfileReq(http.Controller):

    @http.route(['/seochecker/analyze'], type="http", auth="user", website=True,  csrf=False)
    def seochecker_analyze(self,**kw):
        #result = http.request.env['seochecker.profile'].sudo().search([["website","=",kw.get('website_name_input')]],limit=1)
        unique_uuid = uuid.uuid4()
        keywords = kw.get('keyword_1_input') + "," + kw.get('keyword_2_input') + "," + kw.get('keyword_3_input')
        seochecker = http.request.env['seochecker.profile'].sudo().create({
                'name': kw.get('website_name_input'),
                'website': kw.get('website_name_input'),
                'keywords': keywords,
                'user': request.env.user.id,
                'country_id': kw.get('country_input'),
                'language_id': kw.get('language_input'),
                'uuid': unique_uuid,
                'main_website': True
            })
        return request.redirect("/seo-results?token=" + str(unique_uuid))


    @http.route('/carqr/profile/form', type="http", auth="public", website=True,  csrf=False)
    def create_seochecker_profile(self, **kw):
        print("Data Received.....", kw)
        # seochecker_vals = {
        #      'card_id': kw.get('from_id'),
        #      'to': kw.get('to_id'),
        #      'currency': kw.get('currency_id')
        #  }
        result = http.request.env['res.users'].sudo().search(["|",["login","=",kw.get('login')],["x_card_id","=",kw.get('x_card_id')]],limit=1)
        if result:
            return request.render("website.	website.car-profile-error", {'obj': kw})
        else:
            contact = request.env['res.users'].sudo().create(kw)
            return request.render("website.car-profile-create-thanks", {'obj': kw})
        
    @http.route('/userprofile1', type="http", auth="public", website=True,  csrf=False)
    def create_user_profile_1(self, **kw):
        # seochecker_vals = {
        #      'card_id': kw.get('from_id'),
        #      'to': kw.get('to_id'),
        #      'currency': kw.get('currency_id')
        #  }
        result = http.request.env['res.users'].sudo().search([["login","=",kw.get('login')]],limit=1)
        if result:
            return request.render("website.contactus_thanks_ea2f2e_70ad58", {'obj': kw})
        else:
            contact = request.env['res.users'].sudo().create(kw)
            return request.render("website.contactus_thanks_ea2f2e", {'obj': kw})



    # @http.route(['/create/report-for-device'], type="json", auth="public", methods=["POST"], csrf=False)
    # def create_device_req_1(self, **kw):
    #     print("Data Received.....", kw)  
    #     return "hello"
    
    # @http.route('/my_module/xxx', type='json', auth='none', methods=['POST']) 
    # def my_foo(self, **post):
    #     data = request.jsonrequest
    #     return data