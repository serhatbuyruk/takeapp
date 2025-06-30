# -*- coding: utf-8 -*-
from odoo import api, fields, models, tools
from odoo import http
from odoo.http import request
from datetime import datetime
import logging
import requests
_logger = logging.getLogger(__name__)

class CustomSnippets(http.Controller):
    @http.route(['/transfer/cart_content'], type='http', auth="public", website=True)
    def cart(self):
        products = request.website.sale_get_order().order_line.product_id
        data = []
        for product in products:
            fields = product.read(['display_name', 'description_sale', 'list_price', 'website_url'])[0];
            fields['image'] = request.env['website'].image_url(product, 'image_512')
            data.append(fields)
        return request.env['ir.ui.view']._render_template('transfer.s_cart_products_card', {'products': data})

class transferProfileReq(http.Controller):
    
    #widget transfer booking
    @http.route('/create/form-1', type="http", auth="public", website=True,  csrf=False)
    def create_form_req_1(self, **kw):
        print("Data Received.....", kw)
        request.env['transfer.profile'].sudo().create(kw)
        vals = {
             'from': kw.get('from_id'),
             'to': kw.get('to_id'),
             'currency': kw.get('currency_id')
         }
         
        result = http.request.env['product.template'].sudo().search(["|","&",["from_id.id","=",kw.get('from_id')],["to_id.id","=",kw.get('to_id')],"&",["from_id.id","=",kw.get('to_id')],["to_id.id","=",kw.get('from_id')]],limit=1)
        if result:
            return request.render("transfer.form_response_1", {'form_1_details': kw, 'product':result})
        else:
            return request.render("transfer.form_response_4", {'form_1_details': kw, 'product':result})
        
    #car select
    @http.route('/create/form-2', type="http", auth="public", website=True,  csrf=False)
    def create_form_req_2(self, **kw):
        vals = {
             'product': kw.get('product_id'),
             'car': kw.get('car_id'),
             'price': kw.get('price'),
             'currency': kw.get('currency_id')
         }
        return request.render("transfer.form_response_2", {'form_2_details': vals})

    #reservation details
    @http.route('/create/form-3', type="http", auth="public", website=True,  csrf=False)
    def create_form_req_3(self, **kw):
        vals = {
             'id_of_product': kw.get('id_of_product'),
             'from_id': kw.get('from_id'),
             'to_id': kw.get('to_id'),
             'currency': kw.get('currency'),
             'going_transfer_date': kw.get('going_transfer_date'),
             'going_transfer_time': kw.get('going_transfer_time'),
             'going_flight_no': kw.get('going_flight_no'),
             'going_destination': kw.get('going_destination'),
             'return_status': kw.get('return_status'),
             'coming_transfer_date': kw.get('coming_transfer_date'),
             'coming_transfer_time': kw.get('coming_transfer_time'),
             'coming_flight_no': kw.get('coming_flight_no'),
             'coming_destination': kw.get('coming_destination'),
             'special_note': kw.get('special_note'),
             'passenger_number': kw.get('passenger_number'),
             'child_number': kw.get('child_number'),
             'baby_number': kw.get('baby_number'),
             'welcome_status': kw.get('welcome_status'),
             'baby_seat_number': kw.get('baby_seat_number'),
             'booster_seat_number': kw.get('booster_seat_number'),
             'stroller_seat_number': kw.get('stroller_seat_number'),
             'promotion_code': kw.get('promotion_code'),
             'customer_name': kw.get('customer_name'),
             'customer_surname': kw.get('customer_surname'),
             'customer_email': kw.get('customer_email'),
             'customer_phone': kw.get('customer_phone'),
             'another_passengers': kw.get('another_passengers'),
             'price': kw.get('price'),
             'car_name': kw.get('car_name'),
             'car_type': kw.get('car_type'),
             'car_id': kw.get('car_id')
         }
        
        partner_id = http.request.env['res.partner'].sudo().search(["&","&",["name","=",vals['customer_name']],["phone","=",vals['customer_phone']],["email","=",vals['customer_email']]])
        if len(partner_id) == 0:
            request.env['res.partner'].sudo().create({
            'name': vals['customer_name'] + " " + vals['customer_surname'],
            'email': vals['customer_email'],
            'phone': vals['customer_phone']
            })
        
        partner_id = http.request.env['res.partner'].sudo().search(["&","&",["name","=",vals['customer_name'] + " " + vals['customer_surname']],["phone","=",vals['customer_phone']],["email","=",vals['customer_email']]])
        from_id = http.request.env['transfer.city'].sudo().search([["name", "=", vals['from_id']]])
        to_id = http.request.env['transfer.city'].sudo().search([["name", "=", vals['to_id']]])
        currency_id = http.request.env['res.currency'].sudo().search([["name", "=", vals['currency']]])
        product = http.request.env['product.template'].sudo().search([["id", "=", vals['id_of_product']]])
        pricelist_id = http.request.env['product.pricelist'].sudo().search([["currency_id.id", "=", currency_id.id]])
        
        sale_order = request.env['sale.order'].sudo().create({
        'partner_id': partner_id.id,
        'pricelist_id': pricelist_id.id,
        'date_order': datetime.now(),
        
        'id_of_product': vals['id_of_product'],
        'from_id': from_id.id,
        'to_id': to_id.id,
        'currency': vals['currency'],
        'going_transfer_date': vals['going_transfer_date'],
        'going_transfer_time': vals['going_transfer_time'],
        'going_flight_no': vals['going_flight_no'],
        'going_destination': vals['going_destination'],
        'return_status': vals['return_status'],
        'coming_transfer_date': vals['coming_transfer_date'],
        'coming_transfer_time': vals['coming_transfer_time'],
        'coming_flight_no': vals['coming_flight_no'],
        'coming_destination': vals['coming_destination'],
        'special_note': vals['special_note'],
        'passenger_number': vals['passenger_number'],
        'child_number': vals['child_number'],
        'baby_number': vals['baby_number'],
        'welcome_status': vals['welcome_status'],
        'baby_seat_number': vals['baby_seat_number'],
        'booster_seat_number': vals['booster_seat_number'],
        'stroller_seat_number': vals['stroller_seat_number'],
        'promotion_code': vals['promotion_code'],
        'customer_name': vals['customer_name'],
        'customer_surname': vals['customer_surname'],
        'customer_email': vals['customer_email'],
        'customer_phone': vals['customer_phone'],
        'another_passengers': vals['another_passengers'],
        'price': vals['price'],
        'car_name': vals['car_name'],
        'car_type': vals['car_type'],
        'car_id': vals['car_id'],
        #"order_line":[(0,0,{"sequence":10,"display_type":False,"product_uom_qty":1,"qty_delivered":0,"qty_delivered_manual":0,"customer_lead":0,"price_unit":vals['price'],"discount":0,"product_id":sale_order_line.product_id.id,"product_template_id":product.id,"name":product.name,"product_uom":1})]
        
        })
        prd = http.request.env['product.product'].sudo().search([["name", "=", product.name]])
        sale_order.write({
            'order_line': [(0,0, {'product_id':prd.id,"name":product.name,"price_unit":vals['price'],"product_uom_qty":1})]
        })
        #product_id = http.request.env['product.product'].search([],limit=1)
        #sale_order_line = request.env['sale.order.line'].create({  
        #                      'product_id': product.id, 
        #                      "name":product.name,
        #                      "price_unit":vals['price'],
        #                      "product_uom_qty":1,
        #                      "order_id":
        #                    })

        return request.render("transfer.form_response_3", {'form_3_details': vals})