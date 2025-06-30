from odoo import tools, fields, models, api,_
from odoo.exceptions import UserError
from odoo.exceptions import ValidationError
import requests
import json
from datetime import datetime
from base64 import b64encode
cookie = "corders"
import math
import time
import random
import string

class cordersProfile(models.Model):
    _name = "corders.profile"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string="Name",tracking=True)
    card_id = fields.Char(string="Card Id")
    sequence = fields.Integer(string="Sequence", default=1)
    # sequence = fields.Selection([('1','1'),('2', '2'),('3', '3'),('4', '4'),('5', '5'),('6', '6'),('7', '7'),('8', '8'),('9', '9'),('10', '10'),('11', '11'),('12', '12'),('13', '13'),('14', '14'),('15', '15'),('16', '16'),('17', '17'),('18', '18'),('19', '19'),('20', '20')],
    #                                string="Sequence", default="1"
    #                                )
    # link_type = fields.Selection([('1','Mobile'),('2', 'Phone'),('3', 'Location'),('4', 'Whatsapp'),('5', 'Instagram')],
    #                                string="Title", default="1"
    #                                )

    order_json = fields.Char(string="Order Json")
    platform = fields.Selection([('yemeksepeti','Yemeksepeti'),('getir','Getir'),('trendyol','Trendyol'),('migros_yemek','Migros Yemek'),('telefon','Telefon'),('kasa','Kasa')],
                                    string="Platform"
                                    )
    siparis_no = fields.Char(string="Sipariş No")
    magaza = fields.Many2one('res.partner', string="Restoran", domain="[('user_role', '=', 'magaza')]")
    vendor = fields.Many2one('res.partner', string="Satıcı", domain="[('user_role', '=', 'magaza')]")
    sale_id = fields.Many2one('sale.order', string="Bağlantılı Satış")
    siparis_tarihi = fields.Datetime(string="Siparis Tarihi", tracking=True)
    siparis_notu = fields.Char(string="Sipariş Notu", tracking=True)
    otomatik_onay = fields.Boolean(string="Otomatik Onay", tracking=True)
    yolcu = fields.Many2one('res.partner', string="Yolcu")
    musteri_adi = fields.Char(string="Müşteri Adı", tracking=True)
    musteri_telefonu = fields.Char(string="Müşteri Telefonu", tracking=True)
    musteri_email = fields.Char(string="Müşteri Email", tracking=True)
    adres = fields.Char(string="Adres", tracking=True)
    adres_tarifi = fields.Char(string="Adres Tarifi", tracking=True)
    hedef_adres = fields.Char(string="Hedef Adres", tracking=True)
    hedef_adres_tarifi = fields.Char(string="Hedef Adres Tarifi", tracking=True)
    bolge = fields.Char(string="Bölge", tracking=True)
    kurye = fields.Many2one('res.partner', string="Sürücü", domain="[('user_role', '=', 'kurye')]", tracking=True, copy=False)
    kurye_telefonu = fields.Char(string="Sürücü Telefonu", tracking=True, copy=False)
    kurye_siparis_durumu = fields.Selection([('onay_bekliyor','Onay Bekliyor'),('onaylandi','Onaylandi'),('restorana_ulasti','Yolcuya Ulaştı'),('siparisi_teslim_aldi','Yolcuyu Teslim Aldı'),('siparisi_teslim_etti','Yolcuyu Teslim Etti'),('siparisi_iptal_etti','İşlemi İptal Etti'),('yonlendirildi','Yönlendirildi')],
                                    string="Sürücü Sipariş Durumu", default="onay_bekliyor", tracking=True, copy=False
                                    )
    siparis_durumu_zamani = fields.Datetime(string="Siparis Durumu Zamanı", tracking=True)
    siparis_durumu = fields.Selection([('onay_bekliyor','Onay Bekliyor'),('onaylandi','Onaylandi'),('hazirlaniyor','Yolcuya Ulaştı'),('yola_cikti','Yola Çıktı'),('teslim_edildi','Yolcu Teslim Edildi'),('iptal_edildi','İşlem İptal Edildi')],
                                    string="Sipariş Durumu", default="onay_bekliyor", tracking=True, copy=False
                                    )
    surucu_atama_tarihi = fields.Datetime(string="Sürücü Atama Tarihi")
    paket_baslangic_tarihi = fields.Datetime(string="Yolculuk Başlangıç Tarihi")
    yolcuya_ulasma_tarihi = fields.Datetime(string="Yolcuya Ulaşma Tarihi")
    paket_teslim_alma_tarihi = fields.Datetime(string="Yolcuyu Teslim Alma Tarihi")
    paket_bitis_tarihi = fields.Datetime(string="Yolcuyu Bırakma Tarihi")
    paket_suresi_dakika = fields.Integer(string="Toplam Yolculuk Süresi (Dk)")
    yolcuyu_bekleme_suresi_dakika = fields.Integer(string="Yolcuyu Bekleme Süresi (Dk)")
    iptal_nedeni = fields.Char(string="İptal Nedeni", tracking=True)
    odeme_yontemi = fields.Selection([('kapida_nakit','Araçta Nakit Ödeme'),('kapida_kredi_karti','Araçta Kredi Kartı'),('online_odendi','Online Ödendi'),('uygulamadan_odendi','Uygulamadan Ödendi')],
                                    string="Ödeme Yöntemi", tracking=True
                                    )
    kurye_odeme_alma_yontemi = fields.Selection([('kapida_nakit','Araçta Nakit Ödeme'),('kapida_kredi_karti','Araçta Kredi Kartı'),('online_odendi','Online Ödendi'),('uygulamadan_odendi','Uygulamadan Ödendi')],
                                    string="Sürücü Ödeme Alma", tracking=True
                                    )
    toplam_siparis_currency = fields.Many2one('res.currency', string='Toplam Sipariş Currency',default=2, tracking=True)
    toplam_siparis_tutari = fields.Monetary(string="Toplam Sipariş Tutarı", currency_field='toplam_siparis_currency', tracking=True)
    indirim_tutari = fields.Monetary(string="İndirim Tutarı", currency_field='toplam_siparis_currency', tracking=True)
    vergi_tutari = fields.Monetary(string="Vergi Tutarı", currency_field='toplam_siparis_currency', tracking=True)

    diger_odeme_yontemi = fields.Char(string="Diğer Ödeme Yöntemi", tracking=True)
    onay_kodu = fields.Char(string="Onay Kodu", tracking=True)
    yolcu_lat = fields.Float(string="Yolcu Lat", digits=(12, 6))
    yolcu_lng = fields.Float(string="Yolcu Lon", digits=(12, 6))
    lat = fields.Float(string="Hedef Lat", digits=(12, 6))
    lng = fields.Float(string="Hedef Lon", digits=(12, 6))
    driver_first_lat = fields.Float(string="Driver First Latitude", digits=(12, 6))
    driver_first_lng = fields.Float(string="Driver First Longitude", digits=(12, 6))
    driver_last_lat = fields.Float(string="Driver Last Latitude", digits=(12, 6))
    driver_last_lng = fields.Float(string="Driver Last Longitude", digits=(12, 6))
    tahmini_mesafe = fields.Float(string="Tahmini Mesafe")
    mesafe = fields.Float(string="Mesafe")
    yon = fields.Char(string="Yönü")
    restoran_paket_mesafesi = fields.Float(string="Restoran-Paket Mesafesi")
    
    tahmini_arac_yolcu_mesafesi = fields.Float(string="Tahmini Araç-Yolcu Mesafesi")
    tahmini_arac_yolcu_suresi = fields.Float(string="Tahmini Araç-Yolcu Süresi")
    arac_yolcu_mesafesi = fields.Float(string="Araç-Yolcu Mesafesi")
    arac_yolcu_suresi = fields.Float(string="Araç-Yolcu Süresi")
    
    tahmini_yolcu_hedef_mesafesi = fields.Float(string="Tahmini Yolcu-Hedef Mesafesi")
    tahmini_yolcu_hedef_suresi = fields.Float(string="Tahmini Yolcu-Hedef Süresi")
    yolcu_hedef_mesafesi = fields.Float(string="Yolcu-Hedef Mesafesi")
    yolcu_hedef_suresi = fields.Float(string="Yolcu-Hedef Süresi")

    tahmini_toplam_mesafe = fields.Float(string="Tahmini Toplam Mesafe")
    tahmini_toplam_sure = fields.Float(string="Tahmini Toplam Süre")
    toplam_mesafe = fields.Float(string="Toplam Mesafe")
    toplam_sure = fields.Float(string="Toplam Süre")

    yol_trafik_seviyesi = fields.Float(string="Yol Trafik Seviyesi")
    
    sonra_teslim_durumu = fields.Boolean(string="İleri Tarihli Yolculuk Durumu", tracking=True)
    sonra_teslim_tarihi = fields.Datetime(string="İleri Tarihli Yolculuk Tarihi")


    visibility = fields.Boolean(string="Visibility", default=True)
    users_can_edit = fields.Many2many('res.users',relation='x_corders_profile_res_users_rel', column1='corders_users_id',column2='res_users_id', string="Users Can Edit")
    card_owner = fields.Many2one('res.partner', string="Card Owner")
    corders_image = fields.Binary(string="Image")
    color = fields.Char(string="Color")

    product_id = fields.Many2one('product.product', string="Product/Service",tracking=True)
    product_status = fields.Selection([('available','Available'),('busy','Busy')],
                                    string="Product Status", default="available"
                                    )
    delivery_details = fields.Char(string="Rezervasyon Notları", tracking=True)
    start_date = fields.Datetime(string="Start Date",tracking=True)
    end_date = fields.Datetime(string="End Date",tracking=True)
    days_interval = fields.Integer(string="Days Interval", tracking=True)
    turkey_entrance_datetime = fields.Datetime(string="Turkey Entrance",tracking=True)
    saleperson = fields.Many2one('res.partner', string="Saleperson",tracking=True)
    gemici = fields.Many2one('res.partner', string="Gemici",tracking=True)
    dealer = fields.Many2one('res.partner', string="Dealer",tracking=True)
    driver_status = fields.Boolean(string="Driver Status", tracking=True)
    driver = fields.Many2one('res.partner', string="Driver",tracking=True)
    car_petrol_status = fields.Selection([('1','1/4'),('2','2/4'),('3','3/4'),('4','4/4')],
                                    string="Car Petrol Status", default="4", tracking=True
                                    )
    contracts_attachment_ids = fields.Many2many('ir.attachment','attachment_rel_contracts','pro_id_contracts','attach_id_contracts', string='Contracts',) 
    
    repeat_count = fields.Integer(string="Repeat Count", tracking=True)
    repeat_status = fields.Boolean(string="Repeat Status", tracking=True)
    repeat_type = fields.Selection([('once','Once'),('day','Day'),('week','Week'),('Month','Month'),('year','Year')],
                                    string="Repeat Type", default="once", tracking=True
                                    )

    pos_entegrasyon_firmasi = fields.Char(string="Pos Entegrasyon firması")
    pos_entegrasyon_id = fields.Char(string="Pos Entegrasyon Id")
    external_app_id = fields.Char(string="External App Id")
    adisyo_status_id = fields.Char(string="Adisyo Status Id")
    adisyo_status = fields.Char(string="Adisyo Status")
    adisyo_payment_method_name = fields.Char(string="Adisyo Payment Method Name")
    adisyo_payment_method_id = fields.Char(string="Adisyo Payment Method Id")
    adisyo_order_number = fields.Char(string="Adisyo Order Number")
    adisyo_order_type_id = fields.Char(string="Adisyo Order Type Id")
    adisyo_order_type = fields.Char(string="Adisyo Order Type")
    adisyo_customer_id = fields.Char(string="Adisyo Customer Id")
    adisyo_integration_order_id = fields.Char(string="Adisyo Integration Order Id")
    adisyo_restaurant_key = fields.Char(string="Adisyo Restaurant Key")
    adisyo_external_app_key = fields.Char(string="Adisyo External App Key")
    adisyo_update_date = fields.Datetime(string="Adisyo Update Date")

    sepettakip_order_id = fields.Char(string="Sepet Takip Order Id")

    yeppos_order_id = fields.Char(string="YepPos Order Id")

    remoteId = fields.Char(string="remoteId")
    remoteShopId = fields.Char(string="remoteShopId")
    orderCode = fields.Char(string="orderCode")


    city = fields.Char(string="Şehir")
    firma = fields.Char(string="Firma")

    baz_price = fields.Monetary(string="Baz", currency_field='sale_price_currency_id', tracking=True)
    promosyon_price = fields.Monetary(string="Promosyon", currency_field='sale_price_currency_id', tracking=True)
    bahsis_price = fields.Monetary(string="Bahşiş", currency_field='sale_price_currency_id', tracking=True)
    toplam_km_price = fields.Monetary(string="Toplam Km Ücreti", currency_field='sale_price_currency_id', tracking=True)
    platform_komisyon_orani = fields.Integer(string="Platform Komisyon Oranı %")
    platform_komisyon_price = fields.Monetary(string="Platform Komisyon Ücreti", currency_field='sale_price_currency_id', tracking=True)
    yuzdelik_kar_orani_price = fields.Monetary(string="Yüzdelik Kar Ücreti", currency_field='sale_price_currency_id', tracking=True)

    kurye_puani = fields.Integer(string="Sürücü Yolculuk Puanı")
    yolcu_puani = fields.Integer(string="Yolcu Yolculuk Puanı")
    yolcu_sayisi = fields.Integer(string="Yolcu Sayısı")
    bagaj_sayisi = fields.Integer(string="Bagaj Sayısı")

    incident_reported = fields.Boolean(string="Olay Bildirildi mi?", help="Bu yolculuk sırasında bir olay bildirimi yapıldı mı?")
    driver_emergency_button_pressed = fields.Boolean(string="Sürücü Panik Butonuna Bastı mı?", help="Yolculuk sırasında sürücü acil durum butonuna bastı mı?")
    customer_emergency_button_pressed = fields.Boolean(string="Yolcu Panik Butonuna Bastı mı?",help="Yolculuk sırasında yolcu acil durum butonuna bastı mı?")
    ride_audio_record_url = fields.Char(string="Ses Kaydı URL", help="Yolculuğa ait ses kaydının URL bağlantısı.")
    camera_snapshot_url = fields.Char(string="Kamera Görüntü URL", help="Yolculuğa ait kameradan alınan görüntü kaydının URL bağlantısı.")

    sale_price_currency_id = fields.Many2one('res.currency', string='Sale Currency',default=2, tracking=True)
    sale_price = fields.Monetary(string="Sürücü Kazancı", currency_field='sale_price_currency_id', tracking=True)
    deposit_price_currency_id = fields.Many2one('res.currency', string='Deposit Currency',default=2, tracking=True)
    deposit_price = fields.Monetary(string="Deposit Price", currency_field='deposit_price_currency_id', tracking=True)
    sale_description = fields.Char(string="Ödeme Açıklaması", tracking=True)
    received_amount_currency_id = fields.Many2one('res.currency', string='Received Amount Currency',default=2, tracking=True)
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
    remaining_amount = fields.Monetary(string="Sürücü Kalan Tutar", currency_field='remaining_amount_currency_id', tracking=True)
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
    attachment_ids = fields.Many2many('ir.attachment','attachment_rel_1','pro_id_1','attach_id_1', string='Attachments',) 
    

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

    @api.model
    def generate_random_code(self):
        """12 haneli, 'a-z', 'A-Z' ve '0-9' içeren rastgele bir kod üretir"""
        characters = string.ascii_letters + string.digits  # 'a-z', 'A-Z' ve '0-9' karakterleri
        random_code = ''.join(random.choices(characters, k=12))
        return random_code

    
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
                    'func': 'order_get_lat_lng',
                    'message': str(last_result),
                }
            )
        )
        return last_result
    
    @api.model
    def adisyo_get_last_orders(self,id,page,minimumUpdateDate,status):
        contact = self.env['res.partner'].sudo().search([('id', '=', int(id))])
        url = "https://ext.adisyo.com/api/External/v2/RecentOrders?page=" + page + "&minimumUpdateDate=" + minimumUpdateDate + "&status=" + status
        payload = ""
        headers = {
        'x-api-key': contact.adisyo_x_api_key,
        'x-api-secret': contact.adisyo_x_api_secret,
        'x-api-consumer': contact.adisyo_x_api_consumer,
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
                    'func': 'adisyo_get_last_orders',
                    'message': str(last_result),
                }
            )
        )
        return True

    @api.model
    def adisyo_get_complated_orders(self,id,page,startDate,includeCancelled,orderType):
        contact = self.env['res.partner'].sudo().search([('id', '=', int(id))])
        url = "https://ext.adisyo.com/api/External/v2/CompletedOrders?page=" + page + "&startDate=" + startDate + "&includeCancelled=" + includeCancelled + "&orderType=" + orderType
        payload = ""
        headers = {
        'x-api-key': contact.adisyo_x_api_key,
        'x-api-secret': contact.adisyo_x_api_secret,
        'x-api-consumer': contact.adisyo_x_api_consumer,
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
                    'func': 'adisyo_get_complated_orders',
                    'message': str(last_result),
                }
            )
        )
        return True

    @api.model
    def siparis_onaylandi_bilgisi(self,id):
        siparis = self.env['corders.profile'].sudo().search([('id', '=', id)])
        if len(siparis) > 0:
            if siparis.pos_entegrasyon_firmasi == False or siparis.pos_entegrasyon_firmasi == "sepettakip" or siparis.pos_entegrasyon_firmasi == "yeppos":
                siparis["siparis_durumu"] = "onaylandi"
            if siparis.pos_entegrasyon_firmasi == "pagate":
                orderId = (siparis.remoteId)
                url = "https://possiweb.com/api/v2/provider/update-order"
                payload = {
                    "order_id": str(orderId),
                    "status_code": "accepted"
                }
                headers = {
                'Content-Type': 'application/json'
                }
                kurye_response = requests.put(url, headers=headers, json=payload)
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
                                'func': 'siparis_onaylandi_bilgisi',
                                'message': "pagate kurye response: " + str(siparis.id) + " - " + str(kurye_response.text),
                            }
                        )
                    )
                if kurye_response.status_code == 200:
                    siparis["siparis_durumu"] = "onaylandi"
        return True

    @api.model
    def siparis_hazirlaniyor_bilgisi(self,id):
        siparis = self.env['corders.profile'].sudo().search([('id', '=', id)])
        if len(siparis) > 0:
            if siparis.pos_entegrasyon_firmasi == False or siparis.pos_entegrasyon_firmasi == "sepettakip" or siparis.pos_entegrasyon_firmasi == "yeppos":
                siparis["siparis_durumu"] = "hazirlaniyor"
            if siparis.pos_entegrasyon_firmasi == "pagate":
                orderId = (siparis.remoteId)
                url = "https://possiweb.com/api/v2/provider/update-order"
                payload = {
                    "order_id": str(orderId),
                    "status_code": "prepared"
                }
                headers = {
                'Content-Type': 'application/json'
                }
                kurye_response = requests.put(url, headers=headers, json=payload)
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
                                'func': 'get_kurye_siparisi_teslim_aldi',
                                'message': "pagate kurye response: " + str(siparis.id) + " - " + str(kurye_response.json()),
                            }
                        )
                    )
                if kurye_response.status_code == 200:
                    siparis["siparis_durumu"] = "hazirlaniyor"

            if siparis.pos_entegrasyon_firmasi == "adisyo" and siparis.pos_entegrasyon_id != False:
                url = "https://ext.adisyo.com/api/External/v2/Prepared"
                payload = {
                    "OrderId": int(siparis.pos_entegrasyon_id)
                }
                headers = {
                    'x-api-key': siparis.magaza.adisyo_x_api_key,
                    'x-api-secret': siparis.magaza.adisyo_x_api_secret,
                    'x-api-consumer': siparis.magaza.adisyo_x_api_consumer,
                    'Content-Type': 'application/json'
                }
                response = requests.post(url, verify=False, headers=headers, json=payload)
                # print the response text (the content of the requested file):
                # return str(x.content)
                # response = x.json()
                # return str(response['jsonrpc'])
                # aşağıdaki işlemle önce json parse edildi sonra 0-52 ye kadar substring yapıldı
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
                            'func': 'siparis_hazirlaniyor_bilgisi',
                            'message': "adisyo siparis hazırlanıyor response: " + str(siparis.id) + " - " + str(response.json()),
                        }
                    )
                )
                if response.json().get("status"):
                    if response.json().get("status") == 100:
                        siparis["siparis_durumu"] = "hazirlaniyor"
        return True

    @api.model
    def siparis_yola_cikti_bilgisi(self,id):
        siparis = self.env['corders.profile'].sudo().search([('id', '=', id)])
        if len(siparis) > 0:
            if siparis.pos_entegrasyon_firmasi == False:
                siparis["siparis_durumu"] = "yola_cikti"
            if siparis.pos_entegrasyon_firmasi == "sepettakip":
                siparis["siparis_durumu"] = "yola_cikti"
                company = self.env['res.company'].sudo().search([["id","=",1]],limit=1)
                url = company.x_sepettakip_url + "/courier-company/order"
                payload = {
                    "order_id": siparis.sepettakip_order_id,
                    "status": "picked_up"
                }
                headers = {
                    'Courier-Company': company.x_sepettakip_courier_company,
                    'Api-Key': company.x_sepettakip_api_key,
                    'Content-Type': 'application/json'
                }
                response = requests.patch(url, verify=False, headers=headers, json=payload, timeout=5)
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
                                'func': 'sepettakip_get_kurye_siparisi_teslim_aldi',
                                'message': "sepettakip kurye picked_up response: " + str(siparis.id) + " - " + str(response),
                            }
                        )
                    )
            if siparis.pos_entegrasyon_firmasi == "pagate":
                orderId = (siparis.remoteId)
                url = "https://possiweb.com/api/v2/provider/update-order"
                payload = {
                    "order_id": str(orderId),
                    "status_code": "shipped"
                }
                headers = {
                'Content-Type': 'application/json',
                'Authorization': siparis.magaza.token
                }
                kurye_response = requests.put(url, headers=headers, json=payload)
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
                                'func': 'siparis_yola_cikti_bilgisi',
                                'message': "pagate kurye response: " + str(siparis.id) + " - " + str(kurye_response.json()),
                            }
                        )
                    )
                if kurye_response.status_code == 200:
                    siparis["siparis_durumu"] = "yola_cikti"
            if siparis.pos_entegrasyon_firmasi == "adisyo" and siparis.pos_entegrasyon_id != False:
                adisyo_kurye_id = int(siparis.magaza.adisyo_kurye_id)
                if adisyo_kurye_id == False:
                    url = "https://ext.adisyo.com/api/External/v2/Couriers"
                    payload = ""
                    headers = {
                    'x-api-key': siparis.magaza.adisyo_x_api_key,
                    'x-api-secret': siparis.magaza.adisyo_x_api_secret,
                    'x-api-consumer': siparis.magaza.adisyo_x_api_consumer,
                    'Content-Type': 'application/json'
                    }
                    kurye_response = requests.get(url, headers=headers, json=payload)
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
                                    'func': 'get_kurye_siparisi_teslim_aldi',
                                    'message': "adisyo kurye response: " + str(siparis.id) + " - " + str(kurye_response.json()),
                                }
                            )
                        )
                    if kurye_response.json().get("status") == 100:
                        if kurye_response.json().get("couriers") and len(kurye_response.json()["couriers"]) > 0:
                            siparis["magaza"]["adisyo_kurye_id"] = str(kurye_response.json().get("couriers")[0]["id"])
                            adisyo_kurye_id = int(siparis.magaza.adisyo_kurye_id)
                
                if adisyo_kurye_id > 0:
                    url = "https://ext.adisyo.com/api/External/v2/OnDelivery"
                    payload = {
                        "OrderId": int(siparis.pos_entegrasyon_id),
                        "CourierId": adisyo_kurye_id
                    }
                    headers = {
                        'x-api-key': siparis.magaza.adisyo_x_api_key,
                        'x-api-secret': siparis.magaza.adisyo_x_api_secret,
                        'x-api-consumer': siparis.magaza.adisyo_x_api_consumer,
                        'Content-Type': 'application/json'
                    }
                    response = requests.post(url, verify=False, headers=headers, json=payload)
                    # print the response text (the content of the requested file):
                    # return str(x.content)
                    # response = x.json()
                    # return str(response['jsonrpc'])
                    # aşağıdaki işlemle önce json parse edildi sonra 0-52 ye kadar substring yapıldı
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
                                'func': 'siparis_yola_cikti_bilgisi',
                                'message': "adisyo yola çıktı response: " + str(siparis.id) + " - " + str(response.json()),
                            }
                        )
                    )
                    if response.json().get("status"):
                        if response.json().get("status") == 100:
                            siparis["siparis_durumu"] = "yola_cikti"
                            return True
        return True

    @api.model
    def siparis_teslim_edildi_bilgisi(self,id):
        siparis = self.env['corders.profile'].sudo().search([('id', '=', id)])
        if len(siparis) > 0:
            if siparis.pos_entegrasyon_firmasi == False:
                siparis["kurye_siparis_durumu"] = "siparisi_teslim_etti"
            if siparis.pos_entegrasyon_firmasi == "sepettakip":
                siparis["siparis_durumu"] = "teslim_edildi"
                company = self.env['res.company'].sudo().search([["id","=",1]],limit=1)
                url = company.x_sepettakip_url + "/courier-company/order"
                payload = {
                    "order_id": siparis.sepettakip_order_id,
                    "status": "delivered"
                }
                headers = {
                    'Courier-Company': company.x_sepettakip_courier_company,
                    'Api-Key': company.x_sepettakip_api_key,
                    'Content-Type': 'application/json'
                }
                response = requests.patch(url, verify=False, headers=headers, json=payload, timeout=5)
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
                                'func': 'sepettakip_get_kurye_siparisi_teslim_etti',
                                'message': "sepettakip kurye delivered response: " + str(siparis.id) + " - " + str(response),
                            }
                        )
                    )
            if siparis.pos_entegrasyon_firmasi == "pagate":
                orderId = (siparis.remoteId)
                url = "https://possiweb.com/api/v2/provider/update-order"
                payload = {
                    "order_id": str(orderId),
                    "status_code": "delivered"
                }
                headers = {
                'Content-Type': 'application/json',
                'Authorization': siparis.magaza.token
                }
                kurye_response = requests.put(url, headers=headers, json=payload)
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
                                'func': 'siparis_teslim_edildi_bilgisi',
                                'message': "pagate kurye response: " + str(siparis.id) + " - " + str(kurye_response.json()),
                            }
                        )
                    )
                if kurye_response.status_code == 200:
                    siparis["siparis_durumu"] = "teslim_edildi"
            if siparis.pos_entegrasyon_firmasi == "adisyo" and siparis.pos_entegrasyon_id != False:
                odeme_yontemi = siparis.odeme_yontemi
                platform = siparis.platform
                adisyo_odeme_id = int(siparis.adisyo_payment_method_id)
                if adisyo_odeme_id > 0:
                    url = "https://ext.adisyo.com/api/External/v2/Deliver"
                    payload = {
                        "OrderId": int(siparis.pos_entegrasyon_id),
                        "PaymentType": adisyo_odeme_id
                    }
                    headers = {
                        'x-api-key': siparis.magaza.adisyo_x_api_key,
                        'x-api-secret': siparis.magaza.adisyo_x_api_secret,
                        'x-api-consumer': siparis.magaza.adisyo_x_api_consumer,
                        'Content-Type': 'application/json'
                    }
                    response = requests.post(url, verify=False, headers=headers, json=payload)
                    # print the response text (the content of the requested file):
                    # return str(x.content)
                    # response = x.json()
                    # return str(response['jsonrpc'])
                    # aşağıdaki işlemle önce json parse edildi sonra 0-52 ye kadar substring yapıldı
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
                                'func': 'siparis_teslim_edildi_bilgisi',
                                'message': "adisyo siparis tamamlandı response: " + str(siparis.id) + " - " + str(response.json()),
                            }
                        )
                    )
                    if response.json().get("status"):
                        if response.json().get("status") == 100 or response.json().get("status") == 756:
                            siparis["kurye_siparis_durumu"] = "siparisi_teslim_etti"
                            return request.render("website.kurye-anasayfa")
        return True

    @api.model
    def siparis_iptal_edildi_bilgisi(self,id):
        siparis = self.env['corders.profile'].sudo().search([('id', '=', id)])
        if len(siparis) > 0:
            if siparis.iptal_nedeni == False:
                raise ValidationError("Lütfen iptal nedenini eksiksiz bir şekilde giriniz! Bu alan sipariş detaylarına girdiğinizde görünecektir!")
            if siparis.pos_entegrasyon_firmasi == False:
                siparis["siparis_durumu"] = "iptal_edildi"
            if siparis.pos_entegrasyon_firmasi == "sepettakip":
                siparis["siparis_durumu"] = "iptal_edildi"
                company = self.env['res.company'].sudo().search([["id","=",1]],limit=1)
                url = company.x_sepettakip_url + "/courier-company/order"
                payload = {
                    "order_id": siparis.sepettakip_order_id,
                    "status": "cancelled"
                }
                headers = {
                    'Courier-Company': company.x_sepettakip_courier_company,
                    'Api-Key': company.x_sepettakip_api_key,
                    'Content-Type': 'application/json'
                }
                response = requests.patch(url, headers=headers, json=payload, timeout=5)
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
                                'func': 'sepettakip_siparis_canceled',
                                'message': "sepettakip siparis canceled response: " + str(siparis.id) + " - " + str(response),
                            }
                        )
                    )
            if siparis.pos_entegrasyon_firmasi == "pagate":
                orderId = (siparis.remoteId)
                url = "https://possiweb.com/api/v2/provider/update-order"
                payload = {
                    "order_id": str(orderId),
                    "status_code": "cancelled"
                }
                headers = {
                'Content-Type': 'application/json'
                }
                kurye_response = requests.put(url, headers=headers, json=payload)
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
                                'func': 'siparis_iptal_edildi_bilgisi',
                                'message': "pagate kurye response: " + str(siparis.id) + " - " + str(kurye_response.json()),
                            }
                        )
                    )
                if kurye_response.status_code == 200:
                    siparis["siparis_durumu"] = "iptal_edildi"
            if siparis.pos_entegrasyon_firmasi == "adisyo" and siparis.pos_entegrasyon_id != False:
                url = "https://ext.adisyo.com/api/External/v2/Cancel"
                payload = {
                    "OrderId": int(siparis.pos_entegrasyon_id),
                    "CancelReason": str(siparis.iptal_nedeni)
                }
                headers = {
                    'x-api-key': siparis.magaza.adisyo_x_api_key,
                    'x-api-secret': siparis.magaza.adisyo_x_api_secret,
                    'x-api-consumer': siparis.magaza.adisyo_x_api_consumer,
                    'Content-Type': 'application/json'
                }
                response = requests.post(url, verify=False, headers=headers, json=payload)
                # print the response text (the content of the requested file):
                # return str(x.content)
                # response = x.json()
                # return str(response['jsonrpc'])
                # aşağıdaki işlemle önce json parse edildi sonra 0-52 ye kadar substring yapıldı
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
                            'func': 'siparis_iptal_edildi_bilgisi',
                            'message': "adisyo siparis iptal edildi response: " + str(siparis.id) + " - " + str(response.json()),
                        }
                    )
                )
                if response.json().get("status"):
                    if response.json().get("status") == 100:
                        siparis["siparis_durumu"] = "iptal_edildi"
        return True
    
    @api.model
    def generate_random_color(self):
        random_color = random.randint(0, 0xFFFFFF)
        hex_color = f'#{random_color:06X}'
        return str(hex_color)
    
    
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
        # return {
        #         'warning': {
        #             'title': "Ödeme Başarılı!",
        #             'message': str(self.received_amount) + str(self.received_amount_currency_id.name) + " Tutarında Ödeme Alındı. Kalan Tutar: " + str(self.remaining_amount) + str(self.remaining_amount_currency_id.name),
        #         }
        #     }

    @api.onchange('deposit_price')
    def deposite_price_calculation(self):
        self["remaining_amount"] = self.sale_price - self.received_amount - self.received_amount_1 - self.received_amount_2 - self.received_amount_3 - self.received_amount_4 - self.received_amount_5 - self.received_amount_6 - self.received_amount_7
        self["received_amount_total"] = self.received_amount + self.received_amount_1 + self.received_amount_2 + self.received_amount_3 + self.received_amount_4 + self.received_amount_5 + self.received_amount_6 + self.received_amount_7
        if self.sale_price > 0 and self.remaining_amount == 0 and self.received_amount > 0:
            self["customer_payment_status"] = "paid"
        if self.sale_price > 0 and self.remaining_amount > 0 and self.received_amount > 0:
            self["customer_payment_status"] = "partial"
        if self.sale_price > 0 and self.remaining_amount > 0 and self.received_amount == 0:
            self["customer_payment_status"] = "not_paid"
        #if self.deposit_price > 0:
        #    self["sale_description"] = self.sale_description + str(datetime.now().strftime("%d-%m-%Y %H:%M")) + " tarihinde " + str(self.deposit_price) + " " + str(self.deposit_price_currency_id.name) + " ödeme alındı.\n"
        # return {
        #         'warning': {
        #             'title': "Deposit Ödemesi Başarılı!",
        #             'message': str(self.deposit_price) + str(self.deposit_price_currency_id.name) + " Tutarında Ödeme Alındı. Kalan Tutar: " + str(self.remaining_amount) + str(self.remaining_amount_currency_id.name),
        #         }
        #     }

    @api.onchange('turkey_entrance_datetime')
    def turkey_entrance_datetime_calculation(self):
        if datetime.today() and self.turkey_entrance_datetime:
            return {
                    'warning': {
                        'title': "Ehliyet Kullanım Tarihi Hesaplandı!",
                        'message': str(180 - (datetime.today() - self.turkey_entrance_datetime).days) + " Gün Sonra Ehliyetin Kullanım Süresi Bitecektir.",
                    }
                }

    @api.onchange('end_date')
    def end_date_calculation(self):
        if self.end_date != False and self.start_date != False:
            self["days_interval"] = int((self.end_date - self.start_date).days)
            # return {
            #         'warning': {
            #             'title': "Ehliyet Kullanım Tarihi Hesaplandı!",
            #             'message': str((self.end_date - self.start_date).days) + " Gün Hesaplanmıştır.",
            #         }
            #     }

    
        

    @api.onchange('commission_rate')
    def commission_calculation(self):
        self["commission_amount"] = self.sale_price * self.commission_rate / 100

    @api.model
    def time_sleep(self):
        time.sleep(6000000)
        return True

    def see_profile(self):
        if len(self.card_id) > 4:
            return { 'name': 'Go to website',
                    'res_model': 'ir.actions.act_url',
                    'type': 'ir.actions.act_url',
                    'target' : 'self',
                    'url': ("/nfc/profile/" + str(self.card_id))
                }
        if len(self.card_id) == 4:
            return { 'name': 'Go to website',
                    'res_model': 'ir.actions.act_url',
                    'type': 'ir.actions.act_url',
                    'target' : 'self',
                    'url': ("/panel/touch/" + str(self.card_id))
                }

    @api.model
    def find_distance(self,lat1, lon1, lat2, lon2):
        lat1_rad = math.radians(lat1)
        lon1_rad = math.radians(lon1)
        lat2_rad = math.radians(lat2)
        lon2_rad = math.radians(lon2)
        
        # Haversine formula
        dlon = lon2_rad - lon1_rad
        dlat = lat2_rad - lat1_rad
        a = math.sin(dlat/2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon/2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
        # Radius of the Earth in meters
        R = 6371000  # meters
        distance = R * c
        return distance

    @api.model
    def yon_tespiti(self, lat1, lon1, lat2, lon2):
        # Enlem ve boylam farklarını hesapla
        delta_lat = lat2 - lat1
        delta_lon = lon2 - lon1

        # Açı hesaplama
        angle = math.degrees(math.atan2(delta_lon, delta_lat))  # Radyan cinsinden açı hesapla

        # Saat yönü açısını bul
        if angle < 0:
            angle += 360  # Negatif açılara 360 ekleyerek saat yönünü düzelt

        return angle

    
    def from_profile(self):
        return {
            'name':_("Products to Process"),
            'view_mode': 'form',
            'view_id': False,
            'view_type': 'form',
            'res_model': 'corders.profile',
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
        #         'url': ("/web/#id=" + str(119) + "&menu_id=284&action=390&model=corders.profile&view_type=form/")
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
    