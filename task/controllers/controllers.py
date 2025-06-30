# -*- coding: utf-8 -*-
from odoo import api, fields, models, tools
from odoo import http
from odoo.http import request, Response
from datetime import datetime
import logging
import requests
import json
_logger = logging.getLogger(__name__)
from odoo.tools import date_utils
import base64

class taskController(http.Controller):
           
    @http.route('/create_project_task', type='http', auth="user", cors='*', methods=['POST'], website=True, csrf=False)
    def create_project_task(self, **kwargs):
        servis_notu = kwargs.get('servis_notu')
        #contacts_id = int(kwargs.get('contacts_id'))
        worker_id = int(kwargs.get('worker'))
        customer_id = int(kwargs.get('customer_id'))
        #user_id =     int(kwargs.get('user_id'))


        # create_project_task metodunu çağırmak
        #task = request.env['project.task'].sudo().create(servis_notu, contacts_id, user_id)
        task = request.env['project.task'].sudo().create({
            'project_id': 8,
            'name': servis_notu,   
            'x_customer': customer_id,         
            'user_ids': [(4, worker_id)],  # 'user_ids' many2many field için doğru formatta olmalı
        })
    
        
        '''create_ir_logging = request.env['ir.logging'].sudo().create({
                    'dbname': "Last Server",
                    'type': 'server',
                    'name': 'odoo.addons.base.models.ir_actions',
                    'level': 'info',
                    'path': 'action',
                    'line': '489',
                    'func': 'lorawan_callback',
                    'message':  str(data)
                })
        '''
        _logger.info('Customer ID doğruıluğu: %s', customer_id)
        _logger.info('Project task created with ID: %s and Name: %s', task.id, task.name)
        

        # işlemden sonra döneceğiniz şablon veya sayfa
        # return request.redirect('/home')
        
        # Başarılı mesajı döndür
        #return http.Response('Task created successfully', status=200)
        return request.redirect('/task')
    
    @http.route('/create_report_task', type='http', auth="user", cors='*', methods=['POST'], website=True, csrf=False)
    def create_report_task(self, **kwargs):

        task_id = int(kwargs.get('task_id'))
        odeme_yontemi = kwargs.get('odeme_yontemi')
        
        x_pesin = False
        x_kredi_karti = False
        x_havale = False
        x_ucretsiz = False
        
        if odeme_yontemi == 'pesin':
            x_pesin = True
        elif odeme_yontemi == 'kredi_karti':
            x_kredi_karti = True
        elif odeme_yontemi == 'havale':
            x_havale = True
        elif odeme_yontemi == 'ucretsiz':
            x_ucretsiz = True           
        
        task = request.env['project.task'].sudo().search([('id', '=', task_id)], limit=1)
        
        if task:

            servis_teknisyen_file = request.httprequest.files.get('servis_teknisyen')
            customer_binary_file = request.httprequest.files.get('customer_binary')
            musteri_imza_file = request.httprequest.files.get('musteri_imza')

            # Dosyaları debug etmek için loglama yapın
            _logger.info('Servis teknisyen file: %s', servis_teknisyen_file)
            _logger.info('Customer binary file: %s', customer_binary_file)
            #_logger.info('Musteri imza file: %s', musteri_imza_file)


            update_vals ={
                'project_id': 8,  
                'x_servis_tipi': kwargs.get('servis_tipi'),
                'x_sistem_calisir_sekilde_teslim_edildi': kwargs.get('sistem_calisti') == 'on',
                'x_sistem_kontrol_edildi': kwargs.get('sistem_kontrol') == 'on',
                'x_uzak_izleme_yapildi': kwargs.get('uzak_izleme') == 'on',
                'x_kullanim_egitimi_verildi': kwargs.get('kullanim_egitimi') == 'on',
                'x_kullanilan_malzemeler': kwargs.get('kullanilan_malzemeler'),
                'x_sistem_tanimi': kwargs.get('sistem_tanimi'),
                'x_yetkili_firma': kwargs.get('yetkili_firma'),
                'x_final_description': kwargs.get('sonuc_aciklamasi'),
                'x_servis_talep_nedeni': kwargs.get('servis_talep_nedeni'),               
                'x_pesin': x_pesin,
                'x_kredi_karti': x_kredi_karti,
                'x_havale': x_havale,
                'x_ucretsiz': x_ucretsiz,
                'x_urun_bedeli': kwargs.get('urun_bedeli'),
                'x_servis_bedeli': kwargs.get('servis_bedeli'),
            }

            if servis_teknisyen_file:
                update_vals['x_servis_teknisyen_photo'] = base64.b64encode(servis_teknisyen_file.read())

            if customer_binary_file:
                update_vals['x_servis_musteri_imza_photo'] = base64.b64encode(customer_binary_file.read())

            """ if musteri_imza_file:
                update_vals['x_musteri_imza'] = base64.b64encode(musteri_imza_file.read()) """

            task.write(update_vals)
           
            return request.redirect('/task')
        
        return http.Response('No task found for the given task ID', status=404)