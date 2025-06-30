from odoo import tools, fields, models, api,_
from odoo.exceptions import UserError
from odoo.exceptions import ValidationError
import requests
import json
from datetime import datetime
from datetime import date
from base64 import b64encode
cookie = "ttsigorta"
import logging
_logger = logging.getLogger(__name__)

class ttsigorta(models.Model):
    _name = "ttsigorta.profile"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "TT Sigorta"

    name = fields.Char(string="Name")
    description = fields.Char(string="Description")
    sequence = fields.Integer(string="Sequence", default=1)
    
    
    
    
    # Yeni Excel 
    
   
    '''
    SİGORTALI
    sigorta ettiren/ ödeyen
    sigorta şirketi
    Departman
    sözleşme/ poliçe no 
    sözleşme statüsü
    başlangıç tarihi 
    ödenen katkıpayı/ prim
    ödeme günü
    ödeme türü 
    ürün 
    plaka
    belge seri
    uavt
    şasi no
    sigortali = fields.Char(string="Sigortalı", tracking=True)
    sigorta_ettiren = fields.Char(string="Sigorta Ettiren / Ödeyen", tracking=True)
    sigorta_sirketi = fields.Char(string="Sigorta Şirketi", tracking=True)
    departman = fields.Char(string="Departman", tracking=True)
    sozlesme_no = fields.Char(string="Sözleşme / Poliçe No", tracking=True)
    sozlesme_statusu = fields.Char(string="Sözleşme Statüsü", tracking=True)
    baslangic_tarihi = fields.Date(string="Başlangıç Tarihi", tracking=True)
    odenen_katkipayi = fields.Float(string="Ödenen Katkıpayı / Prim", tracking=True)
    odeme_gunu = fields.Integer(string="Ödeme Günü", tracking=True)
    odeme_turu = fields.Selection([
        ('nakit', 'Nakit'),
        ('kredi_karti', 'Kredi Kartı'),
        ('havale', 'Havale/EFT')
    ], string="Ödeme Türü", tracking=True)
    urun = fields.Char(string="Ürün", tracking=True)
    plaka = fields.Char(string="Plaka", tracking=True)
    belge_seri = fields.Char(string="Belge Seri", tracking=True)
    uavt = fields.Char(string="UAVT", tracking=True)
    sasi_no = fields.Char(string="Şasi No", tracking=True)
    '''
    sigortali = fields.Char(string="Sigortalı", tracking=True)
    sigorta_ettiren = fields.Char(string="Sigorta Ettiren / Ödeyen", tracking=True)
    sigorta_sirketi = fields.Char(string="Sigorta Şirketi", tracking=True)
    departman = fields.Char(string="Departman", tracking=True)
    sozlesme_no = fields.Char(string="Sözleşme / Poliçe No ", tracking=True)
    sozlesme_statusu = fields.Char(string="Sözleşme Statüsü", tracking=True)
    baslangic_tarihi  = fields.Char(string="Başlangıç Tarihi ", tracking=True)
    odenen_katkipayi = fields.Char(string="Ödenen Katkıpayı / Prim", tracking=True)
    odeme_gunu = fields.Char(string="Ödeme Günü", tracking=True)
    odeme_turu = fields.Char(string="Ödeme Türü", tracking=True)
    urun = fields.Char(string="Ürün", tracking=True)
    plaka = fields.Char(string="Plaka", tracking=True)
    belge_seri = fields.Char(string="Belge Seri", tracking=True)
    uavt = fields.Char(string="UAVT", tracking=True)
    sasi_no = fields.Char(string="Şasi No", tracking=True)










    color = fields.Char(string="Color")

    
    '''
     
    insurance_selection = fields.Selection([('elementer','Elementer'),('health','Health'),('individual_retirement', 'Individual Retirement')],
                                    string="Insurance Selection", default="", tracking=True
                                    )

    elementer_selection = fields.Selection(
        [
            ('oto', 'Araç Sigortaları'),
            ('konut', 'Konut'),
            ('isyeri', 'İşyeri Sigortası')
        ],
        string="Elementer Sigortalar",
        default="", 
        tracking=True
    )

    individual_retirement_selection = fields.Selection(
        [
            ('bireysel', 'Bireysel Emeklilik'),
            ('hayat', 'Hayat'),
            ('ferdi', 'Ferdi Kaza Sigortalaları')
        ],
        string="Bireysel Ememeklik Sigortalar",
        default="", 
        tracking=True
    )

   
    
    company = fields.Many2one('res.partner', string="Company",tracking=True, domain=[('is_company', '=', True)] )
    tur = fields.Char(string="İşlem Türü")
    satan_partaj_adi = fields.Char(string="Satan Partaj Adı")
    orani = fields.Char(string="Oranı")
    satan_partaj_kodu = fields.Char(string="Satan Partaj Kodu")
    acenta = fields.Char(string="Acenta")
    acenta_no = fields.Char(string="Acenta No")
    muhatap = fields.Char(string="Muhatap")
    musteri_notu = fields.Char(string="Müşteri Notu")
    sozlesme_aktarim_mi = fields.Char(string="Sözleşme Aktarım Mı?")
    police_sozlesme_no = fields.Char(string="Poliçe/Sözleşme No")
    police_tarihi = fields.Date(string="Poliçe Tarihi")
    police_sozlesme_statu = fields.Char(string="Poliçe/Sözleşme Statü")
    police_sozlesme_tanzim_tarihi = fields.Date(string="Poliçe/Sözleşme Tanzim Tarihi")
    tanzim_tarihi = fields.Date(string="Tanzim Tarihi")
    referans = fields.Char(string="Referans")
    duzenli_kp_odeme = fields.Char(string="Düzenli KP / Prim Ödeyen Ad Soyad/Şirket")
    odeyen_iletisim_numarasi = fields.Char(string="Ödeyen İletişim Numarası")
    sozlesme_yururluk_tarihi = fields.Date(string="Sözleşme Yürürlük Tarihi")
    tarife_plan_adi = fields.Char(string="Tarife / Plan Adı")
    tarife_plan_numarasi = fields.Char(string="Tarife / Plan Numarası")
    prim_kp_odeme_periyodu = fields.Char(string="Prim/KP Ödeme Periyodu")
    acik_vade_sayisi = fields.Char(string="Açık Vade Sayısı")
    police_sozlesme_acik_vade_tutar = fields.Float(string="Poliçe/Sözleşme Açık Vade Tutar")
    aktarimla_gelen_toplam_tutar = fields.Float(string="Aktarımla Gelen Toplam Tutar")
    aylik_kp_tutar = fields.Char(string="Aylık KP Tutar")
    notlar = fields.Char(string="Not")
    odeyen_firma = fields.Char(string="Ödeyen Şirket Adı")
    product = fields.Char(string="Ürün")
    product_no = fields.Char(string="Ürün Kodu")
    odemme_gunu = fields.Char(string="Ödeme Günü")
    odemme_aciklamasi = fields.Char(string="Ödeme Şekli Açıklaması")
    satan_kanal = fields.Char(string="Satan Kanal Adı")
    satan_eleman = fields.Char(string="Satan Eleman Adı")
    excel_table = fields.Char(string="Excel Tablosu")
    risk = fields.Char(string="Risk")
    ihtiyari_hayat_uretim = fields.Char(string="İhtiyari Hayat Üretim")
    dovizli_urunler_uretim = fields.Char(string="Dövizli Ürünler Üretim")
    ilk_tarife = fields.Char(string="İlk Tarife/Plan Adı")
    ilk_tahsilat_tarihi = fields.Date(string="İlk Tahsilat Tarihi")
    tahsilat_tarihi = fields.Date(string="Tahsilat Tarihi")
    yetki_alani = fields.Char(string="Yetki Alanı")
    gorusme_sekli = fields.Char(string="Görüşme Şekli")
    
    #sube = fields.Char(string="Şube", tracking=True)
    #sube_kodu = fields.Char(string="Şube kodu", tracking=True)
    bolge = fields.Char(string="Bölge", tracking=True)
    odeme_statu = fields.Char(string="Ödeme Statü")
    ozet_tarife = fields.Char(string="Özet Tarife")
    devir_alan_danisman_adi = fields.Char(string="Devir Alan Danışman Adı")
    




    

    

    
    # Araç Sigortaları
    ruhsat = fields.Char(string="Ruhsat", tracking=True)
    phone = fields.Char(string="Telefon", tracking=True)
    #plaka = fields.Char(string="Plaka", tracking=True)
    seri_no = fields.Char(string="Belge Seri No", tracking=True)
    marka = fields.Char(string="Marka", tracking=True)
    model = fields.Char(string="Model", tracking=True)
    araba_yil = fields.Char(string="Yıl", tracking=True)
    arac_tipi = fields.Char(string="Araç Tipi", tracking=True)
    
    car_no = fields.Char(string="Araç Kodu", tracking=True)
    sase_no = fields.Char(string="Şase No", tracking=True)
    kullanim_tarzi = fields.Char(string="Kullanım Tarzı", tracking=True)
    arac_raic_bedel = fields.Float(string="Araç Raiç Bedel", tracking=True)

    tc = fields.Char(string="Bina Sahibi TC kimlik", tracking=True)
    adress = fields.Char(string="Açık adress(UluslararasıAVT)", tracking=True)
    daire_metrekare = fields.Char(string="Daire Metre Karesi", tracking=True)
    bina_yas = fields.Integer(string="Bina Yaşı", tracking=True)
    bina_kat_adet = fields.Integer(string="Binan toplam kat adeti", tracking=True)
    bina_kat = fields.Integer(string="Daire Kaçıncı Katta Olduğu", tracking=True)
    raic_bedel = fields.Float(string="Raiç Eşya bedeli", tracking=True)
    kira_mal_sahibi = fields.Selection(
        [
            ('kira', 'Kira'),           
            ('malsahibi', 'Mal sahibi')
        ],
        string="Kira mı Mal sahibi",
        default="", tracking=True
    )
    ne_is_yapiyor = fields.Char(string="Ne iş yapıyor", tracking=True)
    satmak_istedigi_mal = fields.Char(string="Var ise satmaya sunduğu emtiya mal bedeli", tracking=True)
    demirbas_bedeli = fields.Float(string="Demirbaş Bedeli", tracking=True)
    guvenlik_onlemleri = fields.Char(string="Güvenlik Önlemleri", tracking=True)
    yangin_onlemleri = fields.Char(string="Yangın Önlemleri", tracking=True)
    calisan_sayisi = fields.Integer(string="Çalışan Sayısı", tracking=True)

    sigorta_kaydi = fields.Boolean(string="Daha önceden sigorta kaydı var mı yok mu?", tracking=True)    
    devir = fields.Char(string="Devir Alınan Sağlık Sigorta Şirketi", tracking=True)
    
    sozlesme_kaydi = fields.Boolean(string="Geçmiste sözlemeşmesi var mı?", tracking=True)
    sozlesme_kaydi_yili = fields.Date(string="Kaç yılında başlmamış", tracking=True)
    sozlesme_sayisi = fields.Integer(string="Kaç adet", tracking=True)
    sozlesme_yapilan_sirket = fields.Char(string="Hangi şirket", tracking=True)
    yatirim_butcesi = fields.Float(string="Yatırım Bütçesi", tracking=True)
    
    doviz_mi_tl = fields.Selection(
        [
            ('tl', 'TL'),           
            ('doviz', 'Döviz')
        ],
        string="Döviz Mi? TL Mi?",
        default="", tracking=True
    )
    
    gorusme_tipi = fields.Selection(
        [
            ('visit', 'Ziyaret'),           
            ('phone', 'Telefon'),
            ('mail', 'Mail'),
            ('social', 'Sosyal Medya Reklam'),
            ('google', 'Google Reklam')
        ],
        string="Müşteri Görüşme Tipi",
        default="", tracking=True
    )
    
    satis_durum = fields.Selection(
        [
            ('teklif', 'Teklif Aşamasında'),           
            ('satildi', 'Satıldı')
        ],
        string="Aşama Durumu",
        default="", tracking=True
    )
    
    '''
    




    partner_id = fields.Many2one('res.partner', string="Customer",tracking=True)
    product_id = fields.Many2one('product.product', string="Product/Service",tracking=True)
    saleperson = fields.Many2one('res.partner', string="Saleperson",tracking=True)
    start_date = fields.Datetime(string="Start Date",tracking=True)
    end_date = fields.Datetime(string="End Date",tracking=True)
    delivery_details = fields.Char(string="Delivery Details", tracking=True)
    days_interval = fields.Integer(string="Days Interval", tracking=True)
 
    contracts_attachment_ids = fields.Many2many('ir.attachment', 'attachment_rel_contracts_ttsigorta', 'pro_id_contracts_ttsigorta', 'attach_id_contracts_ttsigorta', string='Contracts', tracking=True)
    
    #attachment_ids = fields.Many2many('ir.attachment','attachment_rel_realestates','pro_id_realestates','attach_id_realestates', string='Attachments',) 
    
    
    repeat_count = fields.Integer(string="Repeat Count", tracking=True)
    repeat_status = fields.Boolean(string="Repeat Status", tracking=True)
    repeat_type = fields.Selection([('once','Once'),('day','Day'),('week','Week'),('Month','Month'),('year','Year')],
                                    string="Repeat Type", default="once", tracking=True
                                    )

    first_payment_date = fields.Datetime(string="First Payment Date", default=fields.Datetime.now, tracking=True)
    next_payment_date = fields.Datetime(string="Next Payment Date",tracking=True)
    last_payment_date = fields.Datetime(string="Last Payment Date",tracking=True)
    sale_price_currency_id = fields.Many2one('res.currency', string='Sale Currency',default=32, tracking=True)
    sale_price = fields.Monetary(string="Sale Price", currency_field='sale_price_currency_id', tracking=True)
    deposit_price_currency_id = fields.Many2one('res.currency', string='Deposit Currency',default=32, tracking=True)
    deposit_price = fields.Monetary(string="Deposit Price", currency_field='deposit_price_currency_id', tracking=True)
    sale_description = fields.Char(string="Sale Description", tracking=True)
    commission_rate = fields.Float(string="Commission Rate", tracking=True)
    commission_amount_currency_id = fields.Many2one('res.currency', string='Commission Currency %',default=32, tracking=True)
    commission_amount = fields.Monetary(string="Commission Amount", currency_field='commission_amount_currency_id', tracking=True)
    
    
    '''
    card_or_cash = fields.Selection(
        [
            ('card', 'Kart'),           
            ('cash', 'Nakit'),            
        ],
        string="Tahsilat Türü",
        default="", tracking=True
    )
    '''
    #payer = fields.Many2one('res.partner',string="Ödeyen Kişi", tracking=True)
    
     
    
    #offer_date = fields.Date(string="Teklif Tarihi",tracking=True)

    received_amount_currency_id = fields.Many2one('res.currency', string='Received Amount Currency',default=32, tracking=True)
    received_amount = fields.Monetary(string="Received Amount", currency_field='received_amount_currency_id', tracking=True)
    
    received_amount_1_currency_id = fields.Many2one('res.currency', string='Received Amount-1 Currency',default=32, tracking=True)
    received_amount_1 = fields.Monetary(string="Received Amount-1", currency_field='received_amount_1_currency_id', tracking=True)
    #received_amount_1 = fields.Monetary(string="Received Amount-1", currency_field='received_amount_currency_id', tracking=True)
    received_amount_2 = fields.Monetary(string="Received Amount-2", currency_field='received_amount_currency_id', tracking=True)
    received_amount_3 = fields.Monetary(string="Received Amount-3", currency_field='received_amount_currency_id', tracking=True)
    received_amount_4 = fields.Monetary(string="Received Amount-4", currency_field='received_amount_currency_id', tracking=True)
    received_amount_5 = fields.Monetary(string="Received Amount-5", currency_field='received_amount_currency_id', tracking=True)
    received_amount_6 = fields.Monetary(string="Received Amount-6", currency_field='received_amount_currency_id', tracking=True)
    received_amount_7 = fields.Monetary(string="Received Amount-7", currency_field='received_amount_currency_id', tracking=True)
    received_amount_8 = fields.Monetary(string="Received Amount-8", currency_field='received_amount_currency_id', tracking=True)
    received_amount_total = fields.Monetary(string="Received Amount Total", currency_field='received_amount_currency_id', tracking=True)
    remaining_amount_currency_id = fields.Many2one('res.currency', string='Remaining Amount Currency',default=32, tracking=True)
    remaining_amount = fields.Monetary(string="Remaining Amount", currency_field='remaining_amount_currency_id', tracking=True)
    
    


    customer_payment_status = fields.Selection([('not_paid','Not Paid'),('in_payment','In Payment'),('paid','Paid'),('partial','Partial'),('reversed','Reversed'),('invoicing_legacy','Invoicing App Legacy')],
                                    string="Customer Payment Status ", default="not_paid", tracking=True
                                    )
    

    @api.onchange('deposit_price')
    def deposite_price_calculation(self):
        self["remaining_amount"] = self.sale_price - self.received_amount - self.received_amount_1 - self.received_amount_2 - self.received_amount_3 - self.received_amount_4 - self.received_amount_5 - self.received_amount_6 - self.received_amount_7 - self.deposit_price
        self["received_amount_total"] = self.received_amount + self.received_amount_1 + self.received_amount_2 + self.received_amount_3 + self.received_amount_4 + self.received_amount_5 + self.received_amount_6 + self.received_amount_7
        if self.sale_price > 0 and self.remaining_amount == 0 and self.received_amount > 0:
            self["customer_payment_status"] = "paid"
        if self.sale_price > 0 and self.remaining_amount > 0 and self.received_amount > 0:
            self["customer_payment_status"] = "partial"
        if self.sale_price > 0 and self.remaining_amount > 0 and self.received_amount == 0:
            self["customer_payment_status"] = "not_paid"

    @api.onchange('end_date')
    def end_date_calculation(self):
        if self.end_date != False and self.start_date != False:
            self["days_interval"] = int((self.end_date - self.start_date).days)

    def from_profile(self):
        return {
            'name':_("Products to Process"),
            'view_mode': 'form',
            'view_id': False,
            'view_type': 'form',
            'res_model': 'realestates.profile',
            'res_id': self.id,
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'target': 'current',
            'domain': '[]'
        }
    
    
    @api.onchange('received_amount','received_amount_1','sale_price','deposit_price')
    def payment_calculation(self):
        self["remaining_amount"] = self.sale_price - self.received_amount - self.received_amount_1 - self.deposit_price
        self["commission_amount"] = self.sale_price * self.commission_rate / 100
        if self.sale_price > 0 and self.remaining_amount == 0 and self.received_amount > 0:
            self["customer_payment_status"] = "paid"
        if self.sale_price > 0 and self.remaining_amount > 0 and self.received_amount > 0:
            self["customer_payment_status"] = "partial"
        if self.sale_price > 0 and self.remaining_amount > 0 and self.received_amount == 0:
            self["customer_payment_status"] = "not_paid"
    
    
    @api.onchange('sale_price_currency_id')
    def sale_currency_changed(self):
        self["deposit_price_currency_id"] = self.sale_price_currency_id.id
        self["received_amount_currency_id"] = self.sale_price_currency_id.id
        self["received_amount_1_currency_id"] = self.sale_price_currency_id.id
        self["remaining_amount_currency_id"] = self.sale_price_currency_id.id

    @api.model
    def check_repeats(data_dict, field_name):
        repeated = []
        for key, values in data_dict.items():
            if len(values) > 1:
                repeated.append(f"{key} ({len(values)} kayıt)")
        if repeated:
            return f"Tekrar eden {field_name}: " + ", ".join(repeated)
        return "Tekrar eden kayıt bulunamadı."



class ResPartner(models.Model):
          
    _inherit = 'res.partner'
          

    # Kişisel Bilgiler
    nationality = fields.Char(string="Vatandaşlık", tracking=True)
    tc = fields.Char(string="TC Kimlik Numarası", tracking=True)
     
        
    
    gender = fields.Selection(
        [
            ('man', 'Erkek'),           
            ('woman', 'Kadın'),            
        ],
        string="Cinsiyet",
        tracking=True
    )
    birth_date = fields.Date(string="Doğum Tarihi", tracking=True)  # Tarih formatında olmalı
    age = fields.Integer(string="Yaş", compute="_compute_age", store=True, tracking=True)  # Yaş otomatik hesaplanacak

    # İş Bilgileri
    job_title = fields.Char(string="Meslek", tracking=True)
    company_name = fields.Char(string="Çalıştığı Firma", tracking=True)
    work_phone = fields.Char(string="İş Telefonu", tracking=True)

    # Banka Bilgileri
    bank_name = fields.Char(string="Banka Adı", tracking=True)
    bank_branch = fields.Char(string="Şube", tracking=True)
    bank_branch_code = fields.Char(string="Şube Kodu", tracking=True)
    account_number = fields.Char(string="Hesap Numarası", tracking=True)
    iban = fields.Char(string="IBAN", tracking=True)
    

    # Finansal ve Sigorta Bilgileri
    monthly_income = fields.Float(string="Aylık Gelir", tracking=True)
    insurance_status = fields.Selection(
        [
            ('active', 'Aktif'),
            ('inactive', 'Pasif'),
            ('retired', 'Emekli')
        ],
        string="Sigorta Durumu",
        tracking=True
    )
    retirement_info = fields.Text(string="Emeklilik Bilgileri", tracking=True)

    # Acil Durum Bilgileri
    emergency_contact = fields.Char(string="Acil Durum Kişisi", tracking=True)
    emergency_contact_phone = fields.Char(string="Acil Durum Kişi Telefonu", tracking=True)

    # Adres Bilgileri
    city = fields.Char(string="İl", tracking=True)
    district = fields.Char(string="İlçe", tracking=True)

    # Müşteri Bilgileri
    customer_number = fields.Char(string="Müşteri No", tracking=True)

    # Many2Many İlişkisi: Müşterinin ilişkili ürünleri
    product_templates = fields.Many2many(
        'product.template',
        relation='res_partner_product_template_rel',
        column1='res_partner_id',
        column2='product_template_id',
        string="Ürünler"
    )

    # Yaş Hesaplama Fonksiyonu
    @api.depends('birth_date')
    def _compute_age(self):
        today = datetime.today()
        
        for rec in self:
            if rec.birth_date:
                rec.age = today.year - rec.birth_date.year - ((today.month, today.day) < (rec.birth_date.month, rec.birth_date.day))
            else:
                rec.age = 0  # Eğer doğum tarihi girilmemişse, yaş 0 olur
        
        
    @api.model
    def update_birthdays(self):
        
        """Her gün çalışan Scheduled Action fonksiyonu"""
        today = date.today()
        
        # Bugün doğum günü olanları bul
        contacts = self.search([
            ("birth_date", "!=", False),  # Doğum tarihi boş olmayanlar
            ("birth_date", "!=", None),
        ])
        
        updated_count = 0  # Güncellenen kişi sayısı

        for contact in contacts:
            if contact.birth_date and contact.birth_date.month == today.month and contact.birth_date.day == today.day:
                contact._compute_age()
                updated_count += 1
                self.env.cr.commit()  # Güncellemeleri veritabanına işle

        # Loglama
        message = f"Bugün doğum günü olan {updated_count} kişinin yaşı güncellendi."
        self.env["ir.logging"].create({
            "name": "Scheduled Action",
            "type": "server",
            "level": "info",
            "dbname": self.env.cr.dbname,
            "message": message,
            "path": "update_birthdays",
            "line": "1",
            "func": "update_birthdays"
        })
        return message    




