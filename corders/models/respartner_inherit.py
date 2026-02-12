from odoo import models, fields

class ResPartnersInherit(models.Model):
    _inherit = 'res.partner'

    contact_color = fields.Char(string="Contact Color")
    user_role = fields.Selection([('kurye','Kurye'),('magaza','Mağaza'),('kurye_firmasi','Kurye firması')],
                                    string="Kullanıcı Tipi"
                                    )

    player_id = fields.Char(string="Player Id")
    tc = fields.Char(string="TC No")
    passport_no = fields.Char(string="Passport No")
    passport_attachment = fields.Many2many('ir.attachment','attachment_rel_2','pro_id_2','attach_id_2', string='Passport Attachments',)
    id_card_attachment = fields.Many2many('ir.attachment','attachment_rel_idcard','pro_id_idcard','attach_id_idcard', string='Id Card Attachments',)
    driver_licence_attachment = fields.Many2many('ir.attachment','attachment_rel_drivelicence','pro_id_drivelicence','attach_id_drivelicence', string='Driver Licence Attachments',)
    arac_ruhsati_attachment = fields.Many2many('ir.attachment','attachment_rel_aracruhsati','pro_id_aracruhsati','attach_id_aracruhsati', string='Araç Ruhsatı Ekleri',)
    psikoteknik_attachment = fields.Many2many('ir.attachment','attachment_rel_psikoteknik','pro_id_psikoteknik','attach_id_psikoteknik', string='Psikoteknik Ekleri',)
    src4_belgesi_attachment = fields.Many2many('ir.attachment','attachment_rel_src4_belgesi','pro_id_src4_belgesi','attach_id_src4_belgesi', string='SRC 4 Ekleri',)
    sozlesme_attachment = fields.Many2many('ir.attachment','attachment_rel_sozlesme_attachment','pro_id_sozlesme_attachment','attach_id_sozlesme_attachment', string='Sözleşme Ekleri',)
    courier_emergency_contact_info = fields.Char(string="Kurye Acil Durum Ulaşılacak Bilgisi")
    dogum_tarihi = fields.Date(string="Doğum Tarihi")
    egitim_durumu = fields.Selection([('ilkogretim','İlköğretim'),('lise','Lise'),('universite','Üniversite')],
                                    string="Eğitim Durumu"
                                    )
    kurye_arac_tipi = fields.Selection([('bisiklet','Bisiklet'),('motorsiklet','Motorsiklet'),('araba','Araba')],
                                    string="Kurye Araç tipi"
                                    )
    faaliyet_gostermek_istedigi_il = fields.Many2one('res.country.state', string="Faaliyet Göstermek İstediği İl", domain="[('country_id.id', '=', 224)]")
    faaliyet_gostermek_istedigi_ilce = fields.Char(string="Faaliyet Göstermek İstediği İlçe")
    sirket_turu = fields.Selection([('sahis','Şahıs'),('limited','Limited'),('sirketim_yok','Şirketim Yok')],
                                    string="Şirket Türü"
                                    )
    efaura_mukellefi_mi = fields.Boolean(string="E-Fatura Mükellefi Mi?")
    cinsiyet = fields.Selection([('erkek','erkek'),('kadın','Kadın')],
                                    string="Cinsiyet"
                                    )
    arac_durumu = fields.Selection([('var','Var'),('yok','Yok'),('yok_ama_alabilirim','Yok Ama Alabilirim')],
                                    string="Araç Durumu"
                                    )
    dagitim_faaliyeti_tecrubesi = fields.Selection([('tecrubesi_var','Tecrübesi Var'),('tecrubesi_yok','Tecrübesi Yok')],
                                    string="Dağıtım Faaliyeti Tecrübesi"
                                    )
    
    courier_mobile_info = fields.Char(string="Kurye Cihaz Bilgisi")
    lat = fields.Float(string="Latitude", digits=(12, 6))
    lng = fields.Float(string="Longitude", digits=(12, 6))
    konum_dogrulugu = fields.Float(string="Konum Doğruluğu")
    son_konum_zamani = fields.Datetime(string="Son Konum Zamanı")
    konum_online = fields.Boolean(string="Konum Online")
    location_frequency = fields.Integer(string="Location Frequency")
    otomatik_onay = fields.Char(string="Otomatik Onay")

    slot_repeat_status = fields.Boolean(string="Slot Tekrarı")
    slot_ucretlendirme_tipi = fields.Selection([('paket','Paket Başı'),('saatlik','Saatlik'),('paket_saat','Paket Başı + Saatlik'),('paket_saat_km','Paket Başı + Saatlik + Km')],
                                    string="Slot Ücretlendirme Tipi", default="paket_saat", tracking=True
                                    )
    currency_id = fields.Many2one('res.currency', string='Currency',default=32, tracking=True)
    paket_basi_ucret = fields.Monetary(string="Paket Başı Ücret", currency_field='currency_id', tracking=True)
    saatlik_ucret = fields.Monetary(string="Saatlik Ücret", currency_field='currency_id', tracking=True)
    kmlik_ucret = fields.Monetary(string="Km Ücreti", currency_field='currency_id', tracking=True)
    yuzdelik_kar_orani = fields.Float(string="Yüzdelik Kar Oranı %", tracking=True)

    restoran_paket_basi_ucret = fields.Monetary(string="Restoran Paket Başı Ücret", currency_field='currency_id', tracking=True)
    restoran_saatlik_ucret = fields.Monetary(string="Restoran Saatlik Ücret", currency_field='currency_id', tracking=True)
    restoran_kmlik_ucret = fields.Monetary(string="Restoran Km Ücreti", currency_field='currency_id', tracking=True)
    restoran_yuzdelik_kar_orani = fields.Float(string="Restoran Yüzdelik Kar Oranı %", tracking=True)
    

    kurye_firmasi = fields.Many2one('res.partner', string="Kurye Firması", domain="[('user_role', '=', 'kurye_firmasi')]")
    
    code = fields.Char(string="Code")
    kurye_durumu = fields.Selection([('musait','Müsait'),('mesgul','Meşgul'),('pakette','Pakette'),('molada','Molada')],
                                    string="Kurye Durumu"
                                    )
    kurye_siparis_puani = fields.Integer(string="Kurye Sipariş Puanı")
    bank_name = fields.Char(string="Banka Adı")
    iban = fields.Char(string="Iban")

    katilim_tarihi = fields.Date(string="Katılım Tarihi")
    contact_puan = fields.Float(string="Puani",default=5)

    restaurant_status = fields.Selection([('acik','Açık'),('kapali','Kapalı'),('yogun','Yoğun')],
                                    string="Restoran Durumu", default="kapali"
                                    )
    kurye_paketi_reddetmebilsin = fields.Boolean(string="Kurye Paketi Reddebilsin", default=False)
    baska_kuryeye_atama_yapabilsin = fields.Boolean(string="Başka Kuryeye Atayabilsin", default=True)
    odeme_degisikligi_yapabilsin = fields.Boolean(string="Ödeme Değişikliği Yapabilsin", default=True)
    atama_bekleyenleri_gorebilsin = fields.Boolean(string="Atama Bekleyenleri Görebilsin")
    mola_alabilsin_mi = fields.Boolean(string="Mola Alabilsin Mi?", default=True)
    max_mola_suresi = fields.Integer(string="Mola Süresi (DK)", default=30)
    kurye_mola_durumu = fields.Boolean(string="Kurye Mola Durumu", default=False)
    mola_kalan_sure = fields.Integer(string="Mola Kalan Süre (DK)")
    anlik_tasinan_paket_sayisi = fields.Integer(string="Anlık Taşınan Paket Sayısı")
    uzerindeki_paket_sayisi = fields.Integer(string="Üzerindeki Paket Sayısı")
    toplam_tasinan_paket = fields.Integer(string="Toplam Taşınan Paket Sayısı")

    akilli_paket_atama = fields.Boolean(string="Akıllı Paket Atama", default=True)
    paketleri_gruplama_suresi = fields.Integer(string="Paket Gruplama Süresi (DK)", default=20)
    atanacak_paketler_arasi_yaricap_mesafesi = fields.Integer(string="Atanacak Paketler Arası Yarıçap Mesafesi (M)", default=1000)
    kurye_max_paket_sayisi = fields.Integer(string="Kuryenin Aynı Anda Taşıyabileceği Maks Paket Sayısı", default=3)
    yol_uzeri_paket_alma_mesafesi = fields.Integer(string="Yol Üzeri Paket Alma Metresi", default=500)

    pos_entegrasyon_firmasi = fields.Selection([('adisyo','Adisyo'),('sepettakip','SepetTakip'),('pagate','Pagate'),('yeppos','YepPos')],
                                    string="Pos Entegrasyon Firması"
                                    )

    adisyo_x_api_secret = fields.Char(string="Adisyo x-api-secret")
    adisyo_x_api_key = fields.Char(string="Adisyo x-api-key")
    adisyo_x_api_consumer = fields.Char(string="Adisyo x-api-consumer")
    last_integration_time = fields.Datetime(string="Last Integration Time")
    adisyo_kurye_id = fields.Char(string="Adisyo Kurye Id")

    sepettakip_bayi_id = fields.Char(string="Sepettakip Bayi Id")
    sepettakip_password = fields.Char(string="Sepettakip Password")

    yeppos_bayi_id = fields.Char(string="YepPos Bayi Id")
    yeppos_url = fields.Char(string="YepPos Url")
    yeppos_api_key = fields.Char(string="YepPos Api Key")

    remoteShopId = fields.Char(string="remoteShopId")
    token = fields.Char(string="Token")

    kullanici_sozlesmesi = fields.Boolean(string="Kullanıcı Sözleşmesi")

    slot_tipi = fields.Selection([('sabit','Sabit Kuryeli'),('bolge','Bölge Tanımlamalı')],
                                    string="Slot Tipi", tracking=True
                                    )
    
    siparis_bildirim_status = fields.Boolean(string="Sipariş Bildirim Alabilsin",default=True)
    siparis_sms_status = fields.Boolean(string="Sipariş Sms Alabilsin",default=False)
    siparis_aramasi_status = fields.Boolean(string="Sipariş Araması Alabilsin",default=False)
    siparis_maili_status = fields.Boolean(string="Sipariş Maili Alabilsin",default=False)

    pazartesi_status = fields.Boolean(string="Pazartesi",default=True)
    sali_status = fields.Boolean(string="Salı",default=True)
    carsamba_status = fields.Boolean(string="Çarşamba",default=True)
    persembe_status = fields.Boolean(string="Perşembe",default=True)
    cuma_status = fields.Boolean(string="Cuma",default=True)
    cumartesi_status = fields.Boolean(string="Cumartesi",default=True)
    pazar_status = fields.Boolean(string="Pazar",default=True)

    today_slot_status = fields.Boolean(string="Today Slot Status",default=False)

    pazartesi_start_date = fields.Datetime(string="Pazartesi Başlangıç")
    sali_start_date = fields.Datetime(string="Salı Başlangıç")
    carsamba_start_date = fields.Datetime(string="Çarşamba Başlangıç")
    persembe_start_date = fields.Datetime(string="Perşembe Başlangıç")
    cuma_start_date = fields.Datetime(string="Cuma Başlangıç")
    cumartesi_start_date = fields.Datetime(string="Cumartesi Başlangıç")
    pazar_start_date = fields.Datetime(string="Pazar Başlangıç")

    pazartesi_end_date = fields.Datetime(string="Pazartesi Bitiş")
    sali_end_date = fields.Datetime(string="Salı Bitiş")
    carsamba_end_date = fields.Datetime(string="Çarşamba Bitiş")
    persembe_end_date = fields.Datetime(string="Perşembe Bitiş")
    cuma_end_date = fields.Datetime(string="Cuma Bitiş")
    cumartesi_end_date = fields.Datetime(string="Cumartesi Bitiş")
    pazar_end_date = fields.Datetime(string="Pazar Bitiş")

    kuryeler = fields.Many2many('res.partner','res_partner_many2many_1','rel_res_partner_many2many_1','res_partner_id_many2many_1', string='Sabit Kuryeler', domain="[('user_role', '=', 'kurye')]")
    yetkili_contacts = fields.Many2many('res.partner','res_partner_many2many_yetkili','rel_res_partner_many2many_yetkili','res_partner_id_many2many_yetkili', string='Yetkili Contacts')
    yetkili_users = fields.Many2many('res.users','res_users_many2many_yetkili','rel_res_users_many2many_yetkili','res_users_id_many2many_yetkili', string='Yetkili Kişiler')
    


    def open_qr_link(self):
        return { 'name': 'Go to website',
                'res_model': 'ir.actions.act_url',
                'type': 'ir.actions.act_url',
                'target' : 'self',
                'url': ("/company-qr?card_id=" + str(self.id))}