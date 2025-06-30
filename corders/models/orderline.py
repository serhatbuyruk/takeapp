# -*- coding: utf-8 -*-

from odoo import models, fields
from datetime import datetime


# Creating Model/Table to Store Doctor Details
# https://www.youtube.com/watch?v=L6MxDR71_1k&list=PLqRRLx0cl0hoJhjFWkFYowveq2Zn55dhM&index=2
class orderProfile(models.Model):
    _name = 'order.profile'
    _description = 'Order Record'

    name = fields.Char("Name")
    currency_id = fields.Many2one('res.currency', string='Currency Id')
    price = fields.Monetary(string="Amount", currency_field='currency_id')
    order_profile_status = fields.Selection([('not_paid','Not Paid'),('in_profile','In Profile'),('paid','Paid'),('partial','Partial'),('reversed','Reversed'),('invoicing_legacy','Invoicing App Legacy')],
                                    string="Customer Profile Status ", default="not_paid", tracking=True
                                    )
    description = fields.Text("Description")
    sequence = fields.Integer(string="Sequence")
    color = fields.Integer(string="Color")

class orderProfileLines(models.Model):
    _name = 'order.profile.lines'
    _description = 'Order Lines Record'

    name = fields.Char("Name")
    adet = fields.Integer("Adet")
    urun = fields.Char("Ürün")
    sale_price_currency_id = fields.Many2one('res.currency', string='Sale Currency',default=32, tracking=True)
    fiyat = fields.Monetary(string="Fiyat", currency_field='sale_price_currency_id', tracking=True)
    tutar = fields.Monetary(string="Tutar", currency_field='sale_price_currency_id', tracking=True)
    aciklama = fields.Text("Açıklama")
    # partner_id = fields.Many2one('res.partner', string="Kurye", domain="[('user_role', '=', 'kurye')]")
    # start_date = fields.Datetime(string="Başlangıç Zamanı")
    # end_date = fields.Datetime(string="Bitiş Zamanı")
    # kurye_yoklamasi = fields.Boolean(string="Yoklama")
    # gecikme_durumu = fields.Boolean(string="Gecikme Durumu")
    # gecikme_dakikasi = fields.Integer(string="Gecikme Dakikası")
    # erken_kapatma = fields.Boolean(string="Erken Kapatma")
    # bitise_kalan_dakika = fields.Integer(string="Bitişe Kalan Dakika")
    # currency_id = fields.Many2one('res.currency', string='Currency Id')
    # price = fields.Monetary(string="Amount", currency_field='currency_id')
    # description = fields.Text("Description")
    # order_profile_status = fields.Selection([('not_paid','Not Paid'),('in_profile','In Profile'),('paid','Paid'),('partial','Partial'),('reversed','Reversed'),('invoicing_legacy','Invoicing App Legacy')],
    #                                 string="Customer Profile Status ", default="not_paid"
    #                                 )
    # date = fields.Datetime(string="Date", default=fields.Datetime.now)
    order_sequence = fields.Integer(string="Sequence")
    sequence = fields.Integer(string="Sequence")
    color = fields.Integer(string="Color")


class realestatesProfileInherit(models.Model):
    _inherit = 'corders.profile'

    order_profile_lines = fields.One2many('order.profile.lines', 'sequence', string='Order Lines',tracking=True)
