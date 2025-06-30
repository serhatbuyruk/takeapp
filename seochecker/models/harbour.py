# -*- coding: utf-8 -*-

from odoo import models, fields


# Creating Model/Table to Store Doctor Details
# https://www.youtube.com/watch?v=L6MxDR71_1k&list=PLqRRLx0cl0hoJhjFWkFYowveq2Zn55dhM&index=2
class harbourCity(models.Model):
    _name = 'harbour.city'
    _description = 'Harbour Record'

    name = fields.Char("Name")
    day_number = fields.Integer(string="Gün Sayısı")
    ardiye_40ft_price = fields.Monetary(string="40 Ft Ücreti", currency_field='currency_id')
    ardiye_20ft_price = fields.Monetary(string="20 FT Ücreti", currency_field='currency_id')
    kapi_cikis_yukleme_indirme = fields.Monetary(string="Kapı Çıkış / Yükleme / İndirme", currency_field='currency_id')
    konteyner_ic_bosaltma_20ft = fields.Monetary(string="K. İç Boşaltma 20FT", currency_field='currency_id')
    konteyner_ic_bosaltma_40ft = fields.Monetary(string="K. İç Boşaltma 40FT", currency_field='currency_id')
    kapi_cikis_yukleme_indirme_ton = fields.Boolean(string="Ton Bazında")
    currency_id = fields.Many2one('res.currency', string='Para Birimi')
    description = fields.Text("Açıklama")
    sequence = fields.Integer(string="Sıra")
    color = fields.Integer(string="Renk")
    
    
