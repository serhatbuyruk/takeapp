# -*- coding: utf-8 -*-

from odoo import models, fields
from datetime import datetime


# Creating Model/Table to Store Doctor Details
# https://www.youtube.com/watch?v=L6MxDR71_1k&list=PLqRRLx0cl0hoJhjFWkFYowveq2Zn55dhM&index=2
class skuryeProfile(models.Model):
    _name = 'skurye.profile'
    _description = 'Skurye Record'

    name = fields.Char("Name")
    currency_id = fields.Many2one('res.currency', string='Currency Id')
    price = fields.Monetary(string="Amount", currency_field='currency_id')
    skurye_profile_status = fields.Selection([('not_paid','Not Paid'),('in_profile','In Profile'),('paid','Paid'),('partial','Partial'),('reversed','Reversed'),('invoicing_legacy','Invoicing App Legacy')],
                                    string="Customer Profile Status ", default="not_paid", tracking=True
                                    )
    description = fields.Text("Description")
    sequence = fields.Integer(string="Sequence")
    color = fields.Integer(string="Color")
    
class skuryeProfileLines(models.Model):
    _name = 'skurye.profile.lines'
    _description = 'Skurye Lines Record'

    name = fields.Char("Name")
    slot_start_date = fields.Datetime(string="Slot Başlangıç Zamanı", copy=False)
    slot_end_date = fields.Datetime(string="Slot Bitiş Zamanı", copy=False)
    partner_id = fields.Many2one('res.partner', string="Kurye", copy=True, domain="[('user_role', '=', 'kurye')]")
    kurye_start_date = fields.Datetime(string="Kurye İş Başlangıcı", copy=False)
    kurye_end_date = fields.Datetime(string="Kurye İş Bitişi", copy=False)
    active = fields.Boolean(string="Aktif", default=True, copy=False)
    kurye_active = fields.Boolean(string="Kurye Aktiflik", default=True, copy=False)
    start_date = fields.Datetime(string="Başlattığı Zaman", copy=False)
    end_date = fields.Datetime(string="Bitirdiği Zaman", copy=False)
    kurye_yoklamasi = fields.Boolean(string="Yoklama", copy=False)
    gecikme_durumu = fields.Boolean(string="Gecikme Durumu", copy=False)
    gecikme_dakikasi = fields.Integer(string="Gecikme Dakikası", copy=False)
    erken_kapatma = fields.Boolean(string="Erken Kapatma", copy=False)
    bitise_kalan_dakika = fields.Integer(string="Bitişe Kalan Dakika", copy=False)
    slot_paket_sayisi = fields.Integer(string="Slot Paket Sayısı", copy=False)
    kurye_calisma_saati = fields.Float(string="Kuryenin Çalıştığı Saat", copy=False)
    
    sale_price_currency_id = fields.Many2one('res.currency', string='Sale Currency',default=32, tracking=True, copy=False)
    sale_price = fields.Monetary(string="Kurye Kazancı", currency_field='sale_price_currency_id', tracking=True, copy=False)
    baz_price = fields.Monetary(string="Baz", currency_field='sale_price_currency_id', tracking=True)
    toplam_km_price = fields.Monetary(string="Toplam Km Ücreti", currency_field='sale_price_currency_id', tracking=True)
    promosyon_price = fields.Monetary(string="Promosyon", currency_field='sale_price_currency_id', tracking=True)
    bahsis_price = fields.Monetary(string="Bahşiş", currency_field='sale_price_currency_id', tracking=True)
    # currency_id = fields.Many2one('res.currency', string='Currency Id')
    # price = fields.Monetary(string="Amount", currency_field='currency_id')
    # description = fields.Text("Description")
    # skurye_profile_status = fields.Selection([('not_paid','Not Paid'),('in_profile','In Profile'),('paid','Paid'),('partial','Partial'),('reversed','Reversed'),('invoicing_legacy','Invoicing App Legacy')],
    #                                 string="Customer Profile Status ", default="not_paid"
    #                                 )
    # date = fields.Datetime(string="Date", default=fields.Datetime.now)
    order_sequence = fields.Integer(string="Sequence")
    sequence = fields.Integer(string="Sequence")
    color = fields.Integer(string="Color")
    
    
class realestatesProfileInherit(models.Model):
    _inherit = 'slots.profile'

    skurye_profile_lines = fields.One2many('skurye.profile.lines', 'sequence', string='Skurye Lines',tracking=True, copy=True)
    