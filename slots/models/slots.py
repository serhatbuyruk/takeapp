from odoo import tools, fields, models, api,_
from odoo.exceptions import UserError
from odoo.exceptions import ValidationError
import requests
import json
from datetime import datetime,timedelta
from base64 import b64encode
cookie = "slots"
import math
import time
import random
import string

class slotsProfile(models.Model):
    _name = "slots.profile"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string="Name")
    code = fields.Char(string="Code")
    sequence = fields.Integer(string="Sequence", default=1)
    slot_sequence = fields.Integer(string="Slot Sequence", default=1)

    magazalar = fields.Many2many('res.partner',relation='x_slots_profile_res_partners_magazalar_rel', column1='slots_res_partners_magazalar_id',column2='res_partners_magazalar_id', string="Restoranlar", domain="[('user_role', '=', 'magaza')]")
    partner_id = fields.Many2one('res.partner', string="Restoran", domain="[('user_role', '=', 'magaza')]")
    kurye = fields.Many2one('res.partner', string="Kurye", domain="[('user_role', '=', 'kurye')]")
    kurye_add_slot_start_date = fields.Datetime(string="Kuryenin Slotu Seçtiği Zaman", copy=False)
    kurye_job_start_date = fields.Datetime(string="Kuryenin İşe Başladığı Zaman", copy=False)
    kurye_job_end_date = fields.Datetime(string="Kuryenin İşi Bitirdiği Zaman", copy=False)
    kurye_calisma_saati = fields.Float(string="Kuryenin Çalıştığı Saat", copy=False)
    kurye_yoklamasi = fields.Boolean(string="Yoklama", copy=False)
    gecikme_durumu = fields.Boolean(string="İşe Gecikme Durumu", copy=False)
    gecikme_dakikasi = fields.Integer(string="İşe Gecikme Dakikası", copy=False)
    erken_kapatma = fields.Boolean(string="İşi Erken Bitirme Durumu", copy=False)
    bitise_kalan_dakika = fields.Integer(string="İşten Erken Çıkma Dakika", copy=False)
    slot_paket_sayisi = fields.Integer(string="Slotta Kuryenin Taşıdığı Paket", copy=False)
    visibility = fields.Boolean(string="Görünürlük", default=True)
    slot_tipi = fields.Selection([('sabit','Sabit Kuryeli'),('bolge','Bölge Tanımlamalı')],
                                    string="Slot Tipi", default="sabit", tracking=True
                                    )
    calisma_gunu = fields.Selection([('pazartesi','Pazartesi'),('sali','Salı'),('carsamba','Çarşamba'),('persembe','Perşembe'),('cuma','Cuma'),('cumartesi','Cumartesi'),('pazar','Pazar')],
                                    string="Çalışma Günü", default="pazartesi", tracking=True
                                    )
    active_status = fields.Boolean(string="Aktiflik Durumu", default=True, copy=False)
    slotu_kurye_secebilsin = fields.Boolean(string="Slotu Kurye Seçebilsin", default=True)
    doluluk_durumu = fields.Boolean(string="Doluluk Durumu")
    kontenjan = fields.Integer(string="Slot Kontenjanı", default=100)
    anlik_slot_kurye_sayisi = fields.Integer(string="Slot Kurye Sayısı", default=0)
    slot_doluluk_orani = fields.Integer(string="Slot Doluluk Oranı", default=0)
    trafik_etkisi = fields.Integer(string="Trafik Etkisi", default=0)
    hava_durumu_etkisi = fields.Integer(string="Hava Durumu Etkisi", default=0)
    #users_can_edit = fields.Many2many('res.users',relation='x_slots_profile_res_users_rel', column1='slots_users_id',column2='res_users_id', string="Users Can Edit")
    slots_image = fields.Binary(string="Image")
    color = fields.Char(string="Color")
    start_date = fields.Datetime(string="Başlangıç Zamanı",copy=True)
    end_date = fields.Datetime(string="Bitiş Zamanı",copy=True)
    dakika_araligi = fields.Integer(string="Dakika Aralığı",copy=False)
    saat_araligi = fields.Float(string="Saat Aralığı",copy=False)
    slot_acik_adresi = fields.Char(string="Slot Açık Adresi")
    lat = fields.Float(string="Latitude", digits=(12, 6))
    lng = fields.Float(string="Longitude", digits=(12, 6))
    slot_yaricapi = fields.Integer(string="Slot Yarıçapı", default=1000)
    slot_repeat_status = fields.Boolean(string="Slot Tekrarı")
    slot_ucretlendirme_tipi = fields.Selection([('paket','Paket Başı'),('saatlik','Saatlik'),('paket_saat','Paket Başı + Saatlik'),('paket_saat_km','Paket Başı + Saatlik + Km')],
                                    string="Slot Ücretlendirme Tipi", default="paket_saat", tracking=True
                                    )
    currency_id = fields.Many2one('res.currency', string='Currency',default=32, tracking=True)
    paket_basi_ucret = fields.Monetary(string="Paket Başı Ücret", currency_field='currency_id', tracking=True, copy=True)
    saatlik_ucret = fields.Monetary(string="Saatlik Ücret", currency_field='currency_id', tracking=True, copy=True)
    kmlik_ucret = fields.Monetary(string="Km Ücreti", currency_field='currency_id', tracking=True, copy=True)
    slot_promosyon_ucret = fields.Monetary(string="Slot Promosyon Ücreti", currency_field='currency_id', tracking=True, copy=True)

    promosyonlu_slot = fields.Boolean(string="Promosyonlu Slot")

    sale_price_currency_id = fields.Many2one('res.currency', string='Sale Currency',default=32, tracking=True)
    sale_price = fields.Monetary(string="Kurye Kazancı", currency_field='sale_price_currency_id', tracking=True)
    deposit_price_currency_id = fields.Many2one('res.currency', string='Deposit Currency',default=32, tracking=True)
    deposit_price = fields.Monetary(string="Deposit Price", currency_field='deposit_price_currency_id', tracking=True)
    sale_description = fields.Char(string="Ödeme Açıklaması", tracking=True)
    received_amount_currency_id = fields.Many2one('res.currency', string='Received Amount Currency',default=32, tracking=True)
    received_amount = fields.Monetary(string="Ödenen Tutar", currency_field='received_amount_currency_id', tracking=True)
    received_amount_1 = fields.Monetary(string="Ödenen Tutar-1", currency_field='received_amount_currency_id', tracking=True)
    received_amount_2 = fields.Monetary(string="Ödenen Tutar-2", currency_field='received_amount_currency_id', tracking=True)
    received_amount_3 = fields.Monetary(string="Ödenen Tutar-3", currency_field='received_amount_currency_id', tracking=True)
    received_amount_4 = fields.Monetary(string="Ödenen Tutar-4", currency_field='received_amount_currency_id', tracking=True)
    received_amount_5 = fields.Monetary(string="Ödenen Tutar-5", currency_field='received_amount_currency_id', tracking=True)
    received_amount_6 = fields.Monetary(string="Ödenen Tutar-6", currency_field='received_amount_currency_id', tracking=True)
    received_amount_7 = fields.Monetary(string="Ödenen Tutar-7", currency_field='received_amount_currency_id', tracking=True)
    received_amount_8 = fields.Monetary(string="Ödenen Tutar-8", currency_field='received_amount_currency_id', tracking=True)
    received_amount_total = fields.Monetary(string="Ödenen Toplam Tutar", currency_field='received_amount_currency_id', tracking=True)
    remaining_amount_currency_id = fields.Many2one('res.currency', string='Remaining Amount Currency',default=32, tracking=True)
    remaining_amount = fields.Monetary(string="Kurye Kalan Tutar", currency_field='remaining_amount_currency_id', tracking=True)
    commission_rate = fields.Float(string="Commission Rate", tracking=True)
    commission_amount_currency_id = fields.Many2one('res.currency', string='Commission Currency %',default=32, tracking=True)
    commission_amount = fields.Monetary(string="Commission Amount", currency_field='commission_amount_currency_id', tracking=True)
    customer_payment_status = fields.Selection([('not_paid','Not Paid'),('in_payment','In Payment'),('paid','Paid'),('partial','Partial'),('reversed','Reversed'),('invoicing_legacy','Invoicing App Legacy')],
                                    string="Customer Payment Status ", default="not_paid", tracking=True
                                    )
    invoice_status = fields.Selection([('draft','Draft'),('posted','Posted'),('canceled','Canceled')],
                                    string="Customer Invoice Status ", default="draft", tracking=True
                                    )
    sale_payment_receiver = fields.Many2one('res.partner', string="Payment Receiver",tracking=True)
    payment_type = fields.Selection(
        [('cash', 'Cash'), ('credit', 'Credit Card'), ('transfer', 'Transfer')],
        string="Payment Type",
    )
    payment_type_1 = fields.Selection(
        [('cash', 'Cash'), ('credit', 'Credit Card'), ('transfer', 'Transfer')],
        string="Payment Type",
    )
    payment_type_2 = fields.Selection(
        [('cash', 'Cash'), ('credit', 'Credit Card'), ('transfer', 'Transfer')],
        string="Payment Type",
    )
    payment_type_3 = fields.Selection(
        [('cash', 'Cash'), ('credit', 'Credit Card'), ('transfer', 'Transfer')],
        string="Payment Type",
    )
    payment_type_4 = fields.Selection(
        [('cash', 'Cash'), ('credit', 'Credit Card'), ('transfer', 'Transfer')],
        string="Payment Type",
    )
    payment_type_5 = fields.Selection(
        [('cash', 'Cash'), ('credit', 'Credit Card'), ('transfer', 'Transfer')],
        string="Payment Type",
    )
    payment_type_6 = fields.Selection(
        [('cash', 'Cash'), ('credit', 'Credit Card'), ('transfer', 'Transfer')],
        string="Payment Type",
    )
    payment_type_7 = fields.Selection(
        [('cash', 'Cash'), ('credit', 'Credit Card'), ('transfer', 'Transfer')],
        string="Payment Type",
    )

    total_cash = fields.Monetary(string="Total Cash", currency_field='sale_price_currency_id', tracking=True)
    total_credit_card = fields.Monetary(
        string="Total Credit Card", currency_field='sale_price_currency_id', tracking=True
    )
    total_transfer = fields.Monetary(
        string="Total Transfer", currency_field='sale_price_currency_id', tracking=True
    )

    @api.onchange('sale_price_currency_id')
    def sale_currency_changed(self):
        self["deposit_price_currency_id"] = self.sale_price_currency_id.id
        self["received_amount_currency_id"] = self.sale_price_currency_id.id
        self["commission_amount_currency_id"] = self.sale_price_currency_id.id
        self["remaining_amount_currency_id"] = self.sale_price_currency_id.id

    @api.onchange('sale_price')
    def payment_calculation(self):
        self["remaining_amount"] = self.sale_price - self.received_amount - self.received_amount_1 - self.received_amount_2 - self.received_amount_3 - self.received_amount_4 - self.received_amount_5 - self.received_amount_6 - self.received_amount_7
        self["received_amount_total"] = self.received_amount + self.received_amount_1 + self.received_amount_2 + self.received_amount_3 + self.received_amount_4 + self.received_amount_5 + self.received_amount_6 + self.received_amount_7
        if self.sale_price > 0 and self.remaining_amount == 0 and self.received_amount > 0:
            self["customer_payment_status"] = "paid"
        if self.sale_price > 0 and self.remaining_amount > 0 and self.received_amount > 0:
            self["customer_payment_status"] = "partial"
        if self.sale_price > 0 and self.remaining_amount > 0 and self.received_amount == 0:
            self["customer_payment_status"] = "not_paid"
    
    @api.onchange('received_amount','received_amount_1','received_amount_2','received_amount_3','received_amount_4','received_amount_5','received_amount_6','received_amount_7')
    def received_amount_calculation(self):
        self["remaining_amount"] = self.sale_price - self.received_amount - self.received_amount_1 - self.received_amount_2 - self.received_amount_3 - self.received_amount_4 - self.received_amount_5 - self.received_amount_6 - self.received_amount_7
        self["received_amount_total"] = self.received_amount + self.received_amount_1 + self.received_amount_2 + self.received_amount_3 + self.received_amount_4 + self.received_amount_5 + self.received_amount_6 + self.received_amount_7
        if self.sale_price > 0 and self.remaining_amount == 0 and self.received_amount > 0:
            self["customer_payment_status"] = "paid"
        if self.sale_price > 0 and self.remaining_amount > 0 and self.received_amount > 0:
            self["customer_payment_status"] = "partial"
        if self.sale_price > 0 and self.remaining_amount > 0 and self.received_amount == 0:
            self["customer_payment_status"] = "not_paid"

    @api.onchange('partner_id')
    def on_change_partner_id(self):
        self["name"] = self.partner_id.name

    @api.model
    def generate_code(self,length):
        characters = string.ascii_uppercase + string.digits  # Uppercase letters and digits
        return ''.join(random.choice(characters) for _ in range(length))

    @api.model
    def convert_string_to_datetime(self,date_string):
        if date_string:
            date_format = "%Y-%m-%d %H:%M:%S.%f"  # Update the format accordingly
            date_object = datetime.strptime(date_string, date_format)
            date_object = date_object - timedelta(hours = 3)
            return {'year': str(date_object.year),'month': str(date_object.month),'day': str(date_object.day)}
        if date_string == False:
            return False

    @api.model
    def get_lat_lng(self,id,address):
        company = self.env['res.company'].sudo().search([('id', '=', 1)])   
        url = "https://maps.googleapis.com/maps/api/geocode/json?address=" + address + "&key=" + company.x_google_maps_geocode_api_key
        payload = ""
        headers = {
        'Content-Type': 'application/json'
        }
        response = requests.request("GET", url, headers=headers, data=payload)
        last_result = response.json()
        create_ir_logging = (
            self.env['ir.logging']
            .sudo()
            .create(
                {
                    'dbname': "Last Server",
                    'type': 'server',
                    'name': 'odoo.addons.base.models.ir_actions',
                    'level': 'info',
                    'path': 'action',
                    'line': '489',
                    'func': 'get_lat_lng',
                    'message': str(last_result),
                }
            )
        )
        return last_result

    # product_id = fields.Many2one('product.product', string="Product/Service",tracking=True)
    # product_status = fields.Selection([('available','Available'),('busy','Busy')],
    #                                 string="Product Status", default="available"
    #                                 )
    #delivery_details = fields.Char(string="Rezervasyon Notları", tracking=True)
    

    #turkey_entrance_datetime = fields.Datetime(string="Turkey Entrance",tracking=True)
    # saleperson = fields.Many2one('res.partner', string="Saleperson",tracking=True)
    # gemici = fields.Many2one('res.partner', string="Gemici",tracking=True)
    # dealer = fields.Many2one('res.partner', string="Dealer",tracking=True)
    # driver_status = fields.Boolean(string="Driver Status", tracking=True)
    # driver = fields.Many2one('res.partner', string="Driver",tracking=True)
    # car_petrol_status = fields.Selection([('1','1/4'),('2','2/4'),('3','3/4'),('4','4/4')],
    #                                 string="Car Petrol Status", default="4", tracking=True
    #                                 )
    #contracts_attachment_ids = fields.Many2many('ir.attachment','attachment_rel_contracts_slots','pro_id_contracts_slots','attach_id_contracts_slots', string='Contracts',) 
    
    # repeat_count = fields.Integer(string="Repeat Count", tracking=True)
    # repeat_status = fields.Boolean(string="Repeat Status", tracking=True)
    # repeat_type = fields.Selection([('once','Once'),('day','Day'),('week','Week'),('Month','Month'),('year','Year')],
    #                                 string="Repeat Type", default="once", tracking=True
    #                                 )
    # sale_price_currency_id = fields.Many2one('res.currency', string='Sale Currency',default=32, tracking=True)
    # sale_price = fields.Monetary(string="Sale Price", currency_field='sale_price_currency_id', tracking=True)
    # deposit_price_currency_id = fields.Many2one('res.currency', string='Deposit Currency',default=32, tracking=True)
    # deposit_price = fields.Monetary(string="Deposit Price", currency_field='deposit_price_currency_id', tracking=True)
    # sale_description = fields.Char(string="Sale Description", tracking=True)
    # received_amount_currency_id = fields.Many2one('res.currency', string='Received Amount Currency',default=32, tracking=True)
    # received_amount = fields.Monetary(string="Received Amount", currency_field='received_amount_currency_id', tracking=True)
    # received_amount_1 = fields.Monetary(string="Received Amount-1", currency_field='received_amount_currency_id', tracking=True)
    # received_amount_2 = fields.Monetary(string="Received Amount-2", currency_field='received_amount_currency_id', tracking=True)
    # received_amount_3 = fields.Monetary(string="Received Amount-3", currency_field='received_amount_currency_id', tracking=True)
    # received_amount_4 = fields.Monetary(string="Received Amount-4", currency_field='received_amount_currency_id', tracking=True)
    # received_amount_5 = fields.Monetary(string="Received Amount-5", currency_field='received_amount_currency_id', tracking=True)
    # received_amount_6 = fields.Monetary(string="Received Amount-6", currency_field='received_amount_currency_id', tracking=True)
    # received_amount_7 = fields.Monetary(string="Received Amount-7", currency_field='received_amount_currency_id', tracking=True)
    # received_amount_8 = fields.Monetary(string="Received Amount-8", currency_field='received_amount_currency_id', tracking=True)
    # received_amount_total = fields.Monetary(string="Received Amount Total", currency_field='received_amount_currency_id', tracking=True)
    # remaining_amount_currency_id = fields.Many2one('res.currency', string='Remaining Amount Currency',default=32, tracking=True)
    # remaining_amount = fields.Monetary(string="Remaining Amount", currency_field='remaining_amount_currency_id', tracking=True)
    # commission_rate = fields.Float(string="Commission Rate", tracking=True)
    # commission_amount_currency_id = fields.Many2one('res.currency', string='Commission Currency %',default=32, tracking=True)
    # commission_amount = fields.Monetary(string="Commission Amount", currency_field='commission_amount_currency_id', tracking=True)
    # customer_payment_status = fields.Selection([('not_paid','Not Paid'),('in_payment','In Payment'),('paid','Paid'),('partial','Partial'),('reversed','Reversed'),('invoicing_legacy','Invoicing App Legacy')],
    #                                 string="Customer Payment Status ", default="not_paid", tracking=True
    #                                 )
    # invoice_status = fields.Selection([('draft','Draft'),('posted','Posted'),('canceled','Canceled')],
    #                                 string="Customer Invoice Status ", default="draft", tracking=True
    #                                 )
    # sale_payment_receiver = fields.Many2one('res.partner', string="Payment Receiver",tracking=True)
    # sale_payment_type = fields.Selection([('bank','Bank'),('cash','Cash')],
    #                                 string="Payment Type", default="cash", tracking=True
    #                                 )
    # attachment_ids = fields.Many2many('ir.attachment','attachment_rel_1_slots','pro_id_1_slots','attach_id_1_slots', string='Attachments',) 
    

    # scan_date = fields.Datetime(string="Scan Date")
    # entry_date = fields.Datetime(string="Entry Date")
    # exit_date = fields.Datetime(string="Exit Date")
    
    # email = fields.Char(string="Email")
    # tc = fields.Char(string="TC")
    # mobile = fields.Char(string="Mobile")
    # company_id = fields.Many2one('res.company', string="Company")
    # parent_id = fields.Many2one('res.partner', string="Related Company")
    # scan_type = fields.Selection([('entry','Entry'),('exit','Exit'),('mola','Mola')],
    #                                 string="Scan Type ", default=""
    #                                 )
    # lat = fields.Float(string="Latitude", digits=(12, 6))
    # lng = fields.Float(string="Longitude", digits=(12, 6))
    # working_hours = fields.Float(string="Working Hours")
    # working_minutes = fields.Integer(string="Working Minutes")
    # distance = fields.Integer(string="Distance")
    # suspect_level = fields.Integer(string="Suspect Level")
    # suspect_level_entry = fields.Integer(string="Suspect Level Entry")
    # suspect_level_exit = fields.Integer(string="Suspect Level Exit")

    # contact_name = fields.Char(string="Contact Name")
    # company_name = fields.Char(string="Company Name")
    # street = fields.Char(string="Street")
    # city = fields.Char(string="City")
    # state = fields.Many2one('res.country.state', string="State", domain="[('country_id', '=', country_id)]")
    # country_id = fields.Many2one('res.country', string="Country")
    
    # acenta = fields.Char(string="Acenta")

    # product_type = fields.Selection([('araba','Araba'),('yat','Yat'),('bungolov','Bungalov')],
    #                                 string="Ürün Tipi", default="", tracking=True) 
    
    
    # @api.onchange('sale_price_currency_id')
    # def sale_currency_changed(self):
    #     self["deposit_price_currency_id"] = self.sale_price_currency_id.id
    #     self["received_amount_currency_id"] = self.sale_price_currency_id.id
    #     self["commission_amount_currency_id"] = self.sale_price_currency_id.id
    #     self["remaining_amount_currency_id"] = self.sale_price_currency_id.id

    # @api.onchange('sale_price')
    # def payment_calculation(self):
    #     self["remaining_amount"] = self.sale_price - self.received_amount - self.received_amount_1 - self.received_amount_2 - self.received_amount_3 - self.received_amount_4 - self.received_amount_5 - self.received_amount_6 - self.received_amount_7
    #     self["received_amount_total"] = self.received_amount + self.received_amount_1 + self.received_amount_2 + self.received_amount_3 + self.received_amount_4 + self.received_amount_5 + self.received_amount_6 + self.received_amount_7
    #     if self.sale_price > 0 and self.remaining_amount == 0 and self.received_amount > 0:
    #         self["customer_payment_status"] = "paid"
    #     if self.sale_price > 0 and self.remaining_amount > 0 and self.received_amount > 0:
    #         self["customer_payment_status"] = "partial"
    #     if self.sale_price > 0 and self.remaining_amount > 0 and self.received_amount == 0:
    #         self["customer_payment_status"] = "not_paid"
    
    # @api.onchange('received_amount','received_amount_1','received_amount_2','received_amount_3','received_amount_4','received_amount_5','received_amount_6','received_amount_7')
    # def received_amount_calculation(self):
    #     self["remaining_amount"] = self.sale_price - self.received_amount - self.received_amount_1 - self.received_amount_2 - self.received_amount_3 - self.received_amount_4 - self.received_amount_5 - self.received_amount_6 - self.received_amount_7
    #     self["received_amount_total"] = self.received_amount + self.received_amount_1 + self.received_amount_2 + self.received_amount_3 + self.received_amount_4 + self.received_amount_5 + self.received_amount_6 + self.received_amount_7
    #     if self.sale_price > 0 and self.remaining_amount == 0 and self.received_amount > 0:
    #         self["customer_payment_status"] = "paid"
    #     if self.sale_price > 0 and self.remaining_amount > 0 and self.received_amount > 0:
    #         self["customer_payment_status"] = "partial"
    #     if self.sale_price > 0 and self.remaining_amount > 0 and self.received_amount == 0:
    #         self["customer_payment_status"] = "not_paid"
    #     # return {
    #     #         'warning': {
    #     #             'title': "Ödeme Başarılı!",
    #     #             'message': str(self.received_amount) + str(self.received_amount_currency_id.name) + " Tutarında Ödeme Alındı. Kalan Tutar: " + str(self.remaining_amount) + str(self.remaining_amount_currency_id.name),
    #     #         }
    #     #     }

    # @api.onchange('deposit_price')
    # def deposite_price_calculation(self):
    #     self["remaining_amount"] = self.sale_price - self.received_amount - self.received_amount_1 - self.received_amount_2 - self.received_amount_3 - self.received_amount_4 - self.received_amount_5 - self.received_amount_6 - self.received_amount_7
    #     self["received_amount_total"] = self.received_amount + self.received_amount_1 + self.received_amount_2 + self.received_amount_3 + self.received_amount_4 + self.received_amount_5 + self.received_amount_6 + self.received_amount_7
    #     if self.sale_price > 0 and self.remaining_amount == 0 and self.received_amount > 0:
    #         self["customer_payment_status"] = "paid"
    #     if self.sale_price > 0 and self.remaining_amount > 0 and self.received_amount > 0:
    #         self["customer_payment_status"] = "partial"
    #     if self.sale_price > 0 and self.remaining_amount > 0 and self.received_amount == 0:
    #         self["customer_payment_status"] = "not_paid"
    #     #if self.deposit_price > 0:
    #     #    self["sale_description"] = self.sale_description + str(datetime.now().strftime("%d-%m-%Y %H:%M")) + " tarihinde " + str(self.deposit_price) + " " + str(self.deposit_price_currency_id.name) + " ödeme alındı.\n"
    #     # return {
    #     #         'warning': {
    #     #             'title': "Deposit Ödemesi Başarılı!",
    #     #             'message': str(self.deposit_price) + str(self.deposit_price_currency_id.name) + " Tutarında Ödeme Alındı. Kalan Tutar: " + str(self.remaining_amount) + str(self.remaining_amount_currency_id.name),
    #     #         }
    #     #     }

    # @api.onchange('turkey_entrance_datetime')
    # def turkey_entrance_datetime_calculation(self):
    #     if datetime.today() and self.turkey_entrance_datetime:
    #         return {
    #                 'warning': {
    #                     'title': "Ehliyet Kullanım Tarihi Hesaplandı!",
    #                     'message': str(180 - (datetime.today() - self.turkey_entrance_datetime).days) + " Gün Sonra Ehliyetin Kullanım Süresi Bitecektir.",
    #                 }
    #             }

    # @api.onchange('end_date')
    # def end_date_calculation(self):
    #     if self.end_date != False and self.start_date != False:
    #         self["days_interval"] = int((self.end_date - self.start_date).days)
    #         # return {
    #         #         'warning': {
    #         #             'title': "Ehliyet Kullanım Tarihi Hesaplandı!",
    #         #             'message': str((self.end_date - self.start_date).days) + " Gün Hesaplanmıştır.",
    #         #         }
    #         #     }

    
        

    # @api.onchange('commission_rate')
    # def commission_calculation(self):
    #     self["commission_amount"] = self.sale_price * self.commission_rate / 100

    # @api.model
    # def time_sleep(self):
    #     time.sleep(6000000)
    #     return True

    # def see_profile(self):
    #     if len(self.card_id) > 4:
    #         return { 'name': 'Go to website',
    #                 'res_model': 'ir.actions.act_url',
    #                 'type': 'ir.actions.act_url',
    #                 'target' : 'self',
    #                 'url': ("/nfc/profile/" + str(self.card_id))
    #             }
    #     if len(self.card_id) == 4:
    #         return { 'name': 'Go to website',
    #                 'res_model': 'ir.actions.act_url',
    #                 'type': 'ir.actions.act_url',
    #                 'target' : 'self',
    #                 'url': ("/panel/touch/" + str(self.card_id))
    #             }

    # @api.model
    # def find_distance(self,lat1, lon1, lat2, lon2):
    #     lat1_rad = math.radians(lat1)
    #     lon1_rad = math.radians(lon1)
    #     lat2_rad = math.radians(lat2)
    #     lon2_rad = math.radians(lon2)
        
    #     # Haversine formula
    #     dlon = lon2_rad - lon1_rad
    #     dlat = lat2_rad - lat1_rad
    #     a = math.sin(dlat/2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon/2)**2
    #     c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    #     # Radius of the Earth in meters
    #     R = 6371000  # meters
    #     distance = R * c
    #     return distance

    
    def from_profile(self):
        return {
            'name':_("Products to Process"),
            'view_mode': 'form',
            'view_id': False,
            'view_type': 'form',
            'res_model': 'slots.profile',
            'res_id': self.id,
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'target': 'current',
            'domain': '[]'
        }

        # return { 'name': 'Go to Form Profile',
        #         'res_model': 'ir.actions.act_url',
        #         'type': 'ir.actions.act_url',
        #         'target' : 'self',
        #         'url': ("/web/#id=" + str(119) + "&menu_id=284&action=390&model=slots.profile&view_type=form/")
        #        }

    # @api.onchange('device_status','device_status_1','device_status_2','device_status_3','device_status_4','device_status_5')
    # def _get_partner(self):
    #     partner = self.env['res.users'].browse(self.env.uid).partner_id
    #     for rec in self: 
    #         rec.last_action_user = partner.id

    # def write_Link_Status_Active(self):
    #     if self.device_update == False:
    #         self.write({'device_status': 'active'})
    #         self.write({'device_update': True})
    #         partner = self.env['res.users'].browse(self.env.uid).partner_id
    #         for rec in self: 
    #             rec.last_action_user = partner.id
    #     else:
    #         raise ValidationError("Cihaz Son Yaptığınız Ayarları Henüz Almadı. 1 Dakika Sonra Tekrar Deneyiniz.")
        
    # def write_Link_Status_Passive(self):
    #     if self.device_update == False:           
    #         pet = self.env['pets.profile'].sudo().search([["device_id.id","=",self.id]],limit=1)
    #         reports_number = 0
    #         reports = self.env['reports.profile'].search(["&","&","&",["device_id.id","=",self.id],["ademco_id","ilike","E602"],["date",">",pet.registration_date],["date","<",datetime.now()]])
    #         temperature_average = 0
    #         temperature_max = 0
    #         temperature_min = 0
    #         humidity_average = 0
    #         humidity_max = 0
    #         humidity_min = 0
    #         oxygen_average = 0
    #         oxygen_max = 0
    #         oxygen_min = 0
    #         bpm_average = 0
    #         bpm_max = 0
    #         bpm_min = 0
    #         if len(reports) > 0:
    #             reports_number = len(reports)
    #             temperature_average = sum(reports.mapped("sensor_1_value")) / reports_number
    #             temperature_max = max(reports.mapped("sensor_1_value"))
    #             temperature_min = min(reports.mapped("sensor_1_value"))
    #             humidity_average = sum(reports.mapped("sensor_2_value")) / reports_number
    #             humidity_max = max(reports.mapped("sensor_2_value"))
    #             humidity_min = min(reports.mapped("sensor_2_value"))
    #             oxygen_average = sum(reports.mapped("sensor_3_value")) / reports_number
    #             oxygen_max = max(reports.mapped("sensor_3_value"))
    #             oxygen_min = min(reports.mapped("sensor_3_value"))
    #             bpm_average = sum(reports.mapped("sensor_4_value")) / reports_number
    #             bpm_max = max(reports.mapped("sensor_4_value"))
    #             bpm_min = min(reports.mapped("sensor_4_value"))
    #         pet['exit_date'] = datetime.now()
    #         pet['temperature'] = 0
    #         pet['device_id'] = False
    #         pet['values_calculation'] = ("*Süreç Boyunca " + str(round(reports_number,2)) + " Adet Rapor Değerlendirildi. \n*Kabin İçinde Minimum Sıcaklık: " + str(round(temperature_min,2)) +  " Maksimum Sıcaklık: " + str(round(temperature_max,2)) + " Ortalama Sıcaklık : " + str(round(temperature_average,2)) 
    #         + " Olarak Değişti. \n*Kabin İçinde Minimum Nem Oranı: %" + str(round(humidity_min,2)) +  " Maksimum Oksijen Oranı: %" + str(round(humidity_max,2)) + " Ortalama Oksijen Oranı : %" + str(round(humidity_average,2)) + " Olarak Değişti. \n*Kabin İçinde Minimum Oksijen Oranı: %" + str(round(oxygen_min,2)) +  " Maksimum Oksijen Oranı: %" + str(round(oxygen_max,2)) + " Ortalama Oksijen Oranı : %" + str(round(oxygen_average,2)) 
    #         + " Olarak Değişti. \n*Hasta Kalp Atışı; Minimum Bpm: " + str(round(bpm_min,2)) +  " Maksimum Bpm: " + str(round(bpm_max,2)) + " Ortalama Bpm: " + str(round(bpm_average,2)) + " Olarak Değişti.")
    #         self.write({'device_status': 'passive'})
    #         self.write({'device_update': True})
    #         self.write({'pet_id': False})
    #         partner = self.env['res.users'].browse(self.env.uid).partner_id
    #         for rec in self: 
    #             rec.last_action_user = partner.id
    #     else:
    #         raise ValidationError("Cihaz Son Yaptığınız Ayarları Henüz Almadı. 1 Dakika Sonra Tekrar Deneyiniz.")

    # def write_Link_Status_Home(self):
    #     if self.device_update == False:
    #         self.write({'device_status': 'home'})
    #         self.write({'device_update': True})
    #         partner = self.env['res.users'].browse(self.env.uid).partner_id
    #         for rec in self: 
    #             rec.last_action_user = partner.id
    #     else:
    #         raise ValidationError("Cihaz Son Yaptığınız Ayarları Henüz Almadı. 1 Dakika Sonra Tekrar Deneyiniz.")

    # def write_Link_Status_1_Active(self):
    #     if self.device_update == False:
    #         self.write({'device_status_1': 'active'})
    #         self.write({'device_update': True})
    #         partner = self.env['res.users'].browse(self.env.uid).partner_id
    #         for rec in self: 
    #             rec.last_action_user = partner.id
    #     else:
    #         raise ValidationError("Cihaz Son Yaptığınız Ayarları Henüz Almadı. 1 Dakika Sonra Tekrar Deneyiniz.")
        
    # def write_Link_Status_1_Passive(self):
    #     if self.device_update == False:
    #         self.write({'device_status_1': 'passive'})
    #         self.write({'device_update': True})
    #         partner = self.env['res.users'].browse(self.env.uid).partner_id
    #         for rec in self: 
    #             rec.last_action_user = partner.id
    #     else:
    #         raise ValidationError("Cihaz Son Yaptığınız Ayarları Henüz Almadı. 1 Dakika Sonra Tekrar Deneyiniz.")
    
    # def write_Link_Status_2_Active(self):
    #     if self.device_update == False:
    #         self.write({'device_status_2': 'active'})
    #         self.write({'device_update': True})
    #         partner = self.env['res.users'].browse(self.env.uid).partner_id
    #         for rec in self: 
    #             rec.last_action_user = partner.id
    #     else:
    #         raise ValidationError("Cihaz Son Yaptığınız Ayarları Henüz Almadı. 1 Dakika Sonra Tekrar Deneyiniz.")
        
    # def write_Link_Status_2_Passive(self):
    #     if self.device_update == False:
    #         self.write({'device_status_2': 'passive'})
    #         self.write({'device_update': True})
    #         partner = self.env['res.users'].browse(self.env.uid).partner_id
    #         for rec in self: 
    #             rec.last_action_user = partner.id
    #     else:
    #         raise ValidationError("Cihaz Son Yaptığınız Ayarları Henüz Almadı. 1 Dakika Sonra Tekrar Deneyiniz.")
    
    # def write_Link_Status_3_Active(self):
    #     if self.device_update == False:
    #         self.write({'device_status_3': 'active'})
    #         self.write({'device_update': True})
    #         partner = self.env['res.users'].browse(self.env.uid).partner_id
    #         for rec in self: 
    #             rec.last_action_user = partner.id
    #     else:
    #         raise ValidationError("Cihaz Son Yaptığınız Ayarları Henüz Almadı. 1 Dakika Sonra Tekrar Deneyiniz.")
        
    # def write_Link_Status_3_Passive(self):
    #     if self.device_update == False:
    #         self.write({'device_status_3': 'passive'})
    #         self.write({'device_update': True})
    #         partner = self.env['res.users'].browse(self.env.uid).partner_id
    #         for rec in self: 
    #             rec.last_action_user = partner.id
    #     else:
    #         raise ValidationError("Cihaz Son Yaptığınız Ayarları Henüz Almadı. 1 Dakika Sonra Tekrar Deneyiniz.")
    
    # def write_Link_Status_4_Active(self):
    #     if self.device_update == False:
    #         self.write({'device_status_4': 'active'})
    #         self.write({'device_update': True})
    #         partner = self.env['res.users'].browse(self.env.uid).partner_id
    #         for rec in self: 
    #             rec.last_action_user = partner.id
    #     else:
    #         raise ValidationError("Cihaz Son Yaptığınız Ayarları Henüz Almadı. 1 Dakika Sonra Tekrar Deneyiniz.")
        
    # def write_Link_Status_4_Passive(self):
    #     if self.device_update == False:
    #         self.write({'device_status_4': 'passive'})
    #         self.write({'device_update': True})
    #         partner = self.env['res.users'].browse(self.env.uid).partner_id
    #         for rec in self: 
    #             rec.last_action_user = partner.id
    #     else:
    #         raise ValidationError("Cihaz Son Yaptığınız Ayarları Henüz Almadı. 1 Dakika Sonra Tekrar Deneyiniz.")
    
    # def write_Link_Status_5_Active(self):
    #     if self.device_update == False:
    #         self.write({'device_status_5': 'active'})
    #         self.write({'device_update': True})
    #         partner = self.env['res.users'].browse(self.env.uid).partner_id
    #         for rec in self: 
    #             rec.last_action_user = partner.id
    #     else:
    #         raise ValidationError("Cihaz Son Yaptığınız Ayarları Henüz Almadı. 1 Dakika Sonra Tekrar Deneyiniz.")
        
    # def write_Link_Status_5_Passive(self):
    #     if self.device_update == False:
    #         self.write({'device_status_5': 'passive'})
    #         self.write({'device_update': True})
    #         partner = self.env['res.users'].browse(self.env.uid).partner_id
    #         for rec in self: 
    #             rec.last_action_user = partner.id
    #     else:
    #         raise ValidationError("Cihaz Son Yaptığınız Ayarları Henüz Almadı. 1 Dakika Sonra Tekrar Deneyiniz.")
    
    # def create_emergency_report(self):
    #     partner = self.env['res.users'].browse(self.env.uid).partner_id
    #     user_name = "Belirlenemeyen"
    #     for rec in self: 
    #         user_name = partner.name
    #     self.env['reports.profile'].sudo().create({
    #         'name': user_name + " Adlı kullanıcı Acil Durum Çağrısında Bulundu.",
    #         'ademco_id': "B001-000"
    #         })
    # def create_ambulance_report(self):
    #     partner = self.env['res.users'].browse(self.env.uid).partner_id
    #     user_name = "Belirlenemeyen"
    #     for rec in self: 
    #         user_name = partner.name
    #     self.env['reports.profile'].sudo().create({
    #         'name': user_name + " Adlı kullanıcı Ambulans Çağrısında Bulundu.",
    #         'ademco_id': "B002-000"
    #         })
    # def create_fire_report(self):
    #     partner = self.env['res.users'].browse(self.env.uid).partner_id
    #     user_name = "Belirlenemeyen"
    #     for rec in self: 
    #         user_name = partner.name
    #     self.env['reports.profile'].sudo().create({
    #         'name': user_name + " Adlı kullanıcı Yangın Çağrısında Bulundu.",
    #         'ademco_id': "B003-000"
    #         })
        

                            

#discount_percentage = fields.Float("Discount Percentage")

    #gender = fields.Selection([('male','Male'),('female', 'Female'),('other', 'Other'),],string="Gender")
    #type_of_person = fields.Selection([('adult','Adult'),('child', 'Child'),('baby', 'Baby'),('driver', 'Driver')],string="Person Type")
    
    # How to OverRide Create Method Of a Model
    # https://www.youtube.com/watch?v=AS08H3G9x1U&list=PLqRRLx0cl0hoJhjFWkFYowveq2Zn55dhM&index=26
    
    #@api.model
    #def create(self, vals_list):
    #    res = super(ResPartners, self).create(vals_list)
    #    print("yes working")
    #    # do the custom coding here
    #    return res
    