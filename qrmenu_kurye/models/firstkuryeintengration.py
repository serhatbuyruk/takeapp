from odoo import tools, fields, models, api,_
from odoo.exceptions import UserError
from odoo.exceptions import ValidationError
import requests
import json
import logging
from datetime import datetime
from base64 import b64encode
from odoo.tools import html2plaintext
cookie = "qrmenu_kurye"

_logger = logging.getLogger(__name__)

class QrmenuKuryeProfile(models.Model):
    _name = "qrmenu_kurye.profile"

    name = fields.Char(string="Name")
    sequence = fields.Integer(string="Sequence", default=1)
    visibility = fields.Boolean(string="Visibility", default=True)  
    title = fields.Char(string="Title")  
     
    
    
    
class qrmenuProfile(models.Model):
    _inherit = "qrmenu.profile"
    restaurant_id = fields.Integer(string="Restoran ID", help="Restoranın ID bilgisini manuel olarak gireceksiniz.")

    @api.onchange('restaurant_id')
    def _onchange_restaurant_id(self):
        """ Eğer restaurant_id değişirse, tüm sale.order içindeki restaurant_id'leri güncelle """
        if self.restaurant_id:
            # Sale Order içindeki tüm restaurant_id değerlerini güncelle
            sale_orders = self.env['sale.order'].search([('restaurant_id', '!=', self.restaurant_id)])

            if sale_orders:
                sale_orders.write({'restaurant_id': self.restaurant_id})
                _logger.info(f"📌 {len(sale_orders)} adet siparişin restaurant_id değeri güncellendi.")

            # Kullanıcıya popup bildirimi göster
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'Restoran Güncellendi!',
                    'message': f"Tüm siparişlerin restoran ID'si {self.restaurant_id} olarak güncellendi.",
                    'sticky': False,  # Popup otomatik kapanır
                    'type': 'success',  # Bilgi mesajı
                },
            }
    


class SaleOrderInherit(models.Model):
    _inherit = 'sale.order'
    
 
    siparis_durumu = fields.Selection([('onay_bekliyor','Onay Bekliyor'),('onaylandi','Onaylandi'),('hazirlaniyor','Hazirlaniyor'),('yola_cikti','Yola Çıktı'),('teslim_edildi','Teslim Edildi'),('iptal_edildi','İptal Edildi')],
                                string="Sipariş Durumu", default="onay_bekliyor", tracking=True, copy=False
                                )

    musteri_adi = fields.Char(string="Müşteri Adı", compute="_compute_musteri_bilgileri" , tracking=True)
    musteri_telefonu = fields.Char(string="Müşteri Telefonu", compute="_compute_musteri_bilgileri" , tracking=True)
    adres = fields.Text(string="Adres", compute="_compute_musteri_bilgileri" , tracking=True)
    adres_tarifi = fields.Text(string="Adres Tarifi", tracking=True)     
    siparis_notu = fields.Text(string="Sipariş Notu", compute="_compute_siparis_notu" , store=True , tracking=True )
    kurye_cagrildi_mi = fields.Boolean(string="Kurye Çağrıldı mı?", readonly=True, default=False, tracking=True)

    odeme_yontemi = fields.Selection([
        ('kapida_nakit', 'Kapıda Nakit Ödeme'),
        ('kapida_kredi_karti', 'Kapıda Kredi Kartı'),
        ('online_odendi', 'Online Ödendi'),
        ('uygulamadan_odendi', 'Uygulamadan Ödendi')
    ], string="Ödeme Yöntemi", tracking=True)

    toplam_siparis_tutari = fields.Float(string="Toplam Sipariş Tutarı", compute="_compute_toplam_tutar" , tracking=True)
    
    platform = fields.Selection([('yemeksepeti','Yemeksepeti'),('getir','Getir'),('trendyol','Trendyol'),('migros_yemek','Migros Yemek'),('telefon','Telefon'),('kasa','Kasa')],
                                string="Platform", tracking=True
                                )

    magaza = fields.Many2one('res.partner', string="Mağaza")  # Mağaza ID
    restaurant_id = fields.Integer(string="Restoran ID", help="Restoranın ID bilgisini manuel olarak gireceksiniz." , readonly=True, groups="base.group_user")
    # restaurant_id = fields.Integer(string="Restoran ID", compute="_compute_restaurant_id", store=True)
    

    
    
    @api.model
    def default_get(self, fields_list):
        """ Yeni sipariş oluşturulurken restaurant_id'yi otomatik ata """

        # Odoo'nun kendi varsayılan değerlerini al
        defaults = super(SaleOrderInherit, self).default_get(fields_list)  # Üst sınıfın default değerlerini al

        profile = self.env['qrmenu.profile'].search([], limit=1)  # qrmenu.profile içindeki ilk kaydı al

        if profile:
            defaults['restaurant_id'] = profile.restaurant_id  # Eğer kayıt varsa restaurant_id ata
        else:
            # defaults['restaurant_id'] = 0  # Eğer kayıt yoksa 0 ata (veya farklı bir varsayılan değer belirle)
            _logger.error("❌ QR Profil bulunamadı! Restaurant ID zorunludur!")
            raise UserError(_("❌ Restoran ID bulunamadı! Lütfen önce QR Menü Profiline bir restoran ID ekleyin."))

        return defaults
    
    '''
    @api.depends()
    def _compute_restaurant_id(self):
        """ qrmenu.profile içindeki TEK kayıttan restaurant_id'yi çeker """
        profile = self.env['qrmenu.profile'].search([], limit=1)  # İlk kaydı al
        for record in self:
            record.restaurant_id = profile.restaurant_id if profile else 0  # Kayıt varsa restaurant_id ata    
    '''        

    @api.depends('partner_id')
    def _compute_musteri_bilgileri(self):
        _logger.info("🛠️ _compute_musteri_bilgileri METODU ÇALIŞTI! Partner ID değişikliği algılandı.")

        for record in self:
            if not record.partner_id:
                continue  # Eğer partner_id yoksa boş geç

            partner = record.partner_id
            _logger.info("🛠️ Partner ID: %s", partner.id)
            _logger.info("🛠️ Partner Adı: %s", partner.name)

            record.musteri_adi = partner.name or 'Bilinmiyor'
            record.musteri_telefonu = partner.phone or partner.mobile or 'Telefon Yok'

            address_parts = [
                partner.street or '',
                partner.street2 or '',
                f"{partner.city or ''}, {partner.state_id.name or ''} {partner.zip or ''}",
                partner.country_id.name or ''
            ]
            record.adres = "\n".join(filter(bool, address_parts))  # Boş olanları filtreleyerek birleştir

    @api.onchange('partner_id')
    def _onchange_musteri_bilgileri(self):
        if not self.partner_id:
            return

        partner = self.partner_id
        self.musteri_adi = partner.name
        self.musteri_telefonu = partner.phone or partner.mobile
        self.adres = "\n".join(filter(bool, [partner.street, partner.street2, partner.city, partner.state_id.name, partner.zip, partner.country_id.name]))

    @api.depends('amount_total')
    def _compute_toplam_tutar(self):
        """ Toplam sipariş tutarını amount_total değerinden çeker """
        for record in self:
            record.toplam_siparis_tutari = record.amount_total
        
    @api.onchange('amount_total')
    def _onchange_toplam_tutar(self):
        """ Formda amount_total değiştiğinde toplam_siparis_tutari'yi günceller (sadece UI için) """
        for record in self:
            record.toplam_siparis_tutari = record.amount_total            
            
    @api.depends('note')
    def _compute_siparis_notu(self):
        """ note alanını siparis_notu'ya eşitle """
        #for record in self:
        #    record.siparis_notu = record.note or ""  
        for record in self:
            record.siparis_notu = html2plaintext(record.note or "")          
    
    @api.onchange('note')
    def _onchange_siparis_notu(self):
        """ Kullanıcı note alanını değiştirdiğinde siparis_notu'yu günceller """
        for record in self:
            record.siparis_notu = record.note or ""
       

    def action_send_to_corders(self):
        _logger.info("action_send_to_corders test deneme2")
        """
        📌 Butona tıklanınca API'ye sipariş gönderir. Log kayıtlarını ir.logging içine ekler.
        """
        
        # **1️⃣ Eğer kurye zaten çağrıldıysa, tekrar çağrılmasını engelle**
        if self.kurye_cagrildi_mi:            
            _logger.warning("❌ Kurye zaten çağrıldı, tekrar çağrılamaz!")
            self.env['ir.logging'].sudo().create({
                'name': 'Kurye Çağırma Engellendi',
                'type': 'server',
                'dbname': self._cr.dbname,
                'level': 'warning',
                'message': f"⚠️ Sipariş ID: {self.id} için kurye zaten çağrıldı, tekrar çağrılamaz!",
                'path': 'sale.order',
                'line': 'action_send_to_corders',
                'func': 'Kurye Çağrıldı Kontrol'
            })
            #raise UserError(_("Bu sipariş için kurye zaten çağrıldı!"))
            return False # İşlemi durdur

        """ Eğer restaurant_id boşsa kullanıcıya popup mesajı göster """
        if not self.restaurant_id:
            '''
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'Eksik Bilgi!',
                    'message': "Lütfen bir restoran ID girin!",
                    'sticky': False,  # False olursa birkaç saniye sonra kaybolur
                    'type': 'warning',  # warning, success, danger, info
                },
            }
            '''
            '''
            self.env['bus.bus']._sendone(
            self.env.user.partner_id,
                'simple_notification',
                {
                    'type': 'warning',
                    'title': 'Eksik Bilgi!',
                    'message': 'Lütfen bir restoran ID girin!!',
                }
            )
            '''
            #raise UserError("Lütfen bir restoran ID girin!")  # İşlemi durdurur
            
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'Eksik Bilgi!',
                    'message': "Lütfen bir restoran ID seçin!!!",
                    'sticky': False,  # False olursa bir süre sonra kaybolur, True olursa ekranda kalır
                    'type': 'warning',  # info, success, warning, danger
                },
            }
            
        if not self.restaurant_id:  
            return False # İşlemi durdur  

        _logger.info("✅ Restaurant ID dolu, işleme devam ediliyor...")    

        # ✅ Ödeme yöntemi kontrolü
        if not self.odeme_yontemi:
            _logger.error("❌ Ödeme yöntemi seçilmemiş! Kurye çağrılamaz.")
            raise UserError(_("❌ Ödeme yöntemi zorunludur! Kurye çağırmadan önce bir ödeme yöntemi seçmelisiniz."))

        # ✅ Platform kontrolü
        if not self.platform:
            _logger.error("❌ Platform seçilmemiş! Kurye çağrılamaz.")
            raise UserError(_("❌ Platform seçilmelidir! Kurye çağırmadan önce bir platform belirtmelisiniz."))    
        
        ODOO_URL = "https://kuryetec.autoronics.com"
        DB_NAME = "kuryetec"
        USERNAME = "qrmenu"
        PASSWORD = "qrmenu07"

        session = requests.Session()

        # 🛠️ Odoo'ya giriş yap ve session_id al
        login_payload = {
            "jsonrpc": "2.0",
            "params": {
                "login": USERNAME,
                "password": PASSWORD,
                "db": DB_NAME
            }
        }

        login_response = session.post(f"{ODOO_URL}/web/session/authenticate", json=login_payload)

        if login_response.status_code == 200:
            login_data = login_response.json()
            if login_data.get("result"):
                session_id = session.cookies.get("session_id")
                self.env['ir.logging'].sudo().create({
                    'name': 'Odoo Session Girişi',
                    'type': 'server',
                    'dbname': self._cr.dbname,
                    'level': 'info',
                    'message': f"✅ Başarıyla giriş yapıldı! Session ID: {session_id}",
                    'path': 'sale.order',
                    'line': 'action_send_to_corders',
                    'func': 'Login'
                })
            else:
                self.env['ir.logging'].sudo().create({
                    'name': 'Odoo Session Hata',
                    'type': 'server',
                    'dbname': self._cr.dbname,
                    'level': 'error',
                    'message': f"❌ Giriş başarısız: {login_data}",
                    'path': 'sale.order',
                    'line': 'action_send_to_corders',
                    'func': 'Login Error'
                })
                return False
        else:
            self.env['ir.logging'].sudo().create({
                'name': 'Odoo Session HTTP Hatası',
                'type': 'server',
                'dbname': self._cr.dbname,
                'level': 'error',
                'message': f"❌ Giriş sırasında hata oluştu: {login_response.text}",
                'path': 'sale.order',
                'line': 'action_send_to_corders',
                'func': 'Login HTTP Error'
            })
            return False

        # 📌 Sipariş JSON verisini oluştur
        headers = {
            "Content-Type": "application/json",
            "accept": "*/*",
            "cookie": f"session_id={session_id}"
        }

        payload = {
            "id": 30,
            "jsonrpc": "2.0",
            "method": "call",
            "params": {
                "args": [
                    {
                        "siparis_durumu": self.siparis_durumu,
                        "musteri_adi": self.musteri_adi,
                        "musteri_telefonu": self.musteri_telefonu,
                        "adres": self.adres,
                        "adres_tarifi": self.adres_tarifi,
                        "siparis_notu": self.siparis_notu,
                        "odeme_yontemi": self.odeme_yontemi,
                        "toplam_siparis_tutari": self.amount_total,  # Odoo'dan toplam tutarı çekiyoruz
                        "magaza": self.restaurant_id,  
                        "platform": self.platform,
                        "order_profile_lines": [
                            [0, "virtual_4", {
                                "urun": line.product_id.name,
                                "adet": line.product_uom_qty,
                                "fiyat": line.price_unit,
                                "tutar": line.price_subtotal
                            }] for line in self.order_line
                        ]
                    }
                ],
                "model": "corders.profile",
                "method": "create",
                "kwargs": {
                    "context": {
                        "lang": "en_US",
                        "tz": "Turkey",
                        "uid": 2,
                        "allowed_company_ids": [1],
                        "params": {
                            "menu_id": 736,
                            "action": 1062
                        }
                    }
                }
            }
        }
        # 📌 API'ye Sipariş Gönder
        try:
            response = session.post(f"{ODOO_URL}/web/dataset/call_kw/corders.profile/create", json=payload, headers=headers)

            if response.status_code == 200:
                result_data = response.json()
                _logger.info(f"✅ Corders API yanıtı: {json.dumps(result_data, indent=4)}")

                # **Hata olup olmadığını kontrol et**
                if "error" in result_data:
                    error_message = result_data["error"].get("message", "Bilinmeyen hata")
                    _logger.error(f"❌ Corders API Hatası: {error_message}")

                    # **Hata mesajını logla**
                    self.env['ir.logging'].sudo().create({
                        'name': 'CORDERS API Hata',
                        'type': 'server',
                        'dbname': self._cr.dbname,
                        'level': 'error',
                        'message': f"Corders API başarısız! Hata: {json.dumps(result_data, indent=4)}",
                        'path': 'sale.order',
                        'line': 'action_send_to_corders',
                        'func': 'API Error'
                    })

                    return False  # **İşlemi durdur**

                # **Başarıyla dönen sipariş ID'sini al**
                corders_siparis_id = result_data.get("result", None)
                if corders_siparis_id:
                    _logger.info(f"✅ Corders Sipariş ID: {corders_siparis_id}")
                    self.write({
                        'kurye_cagrildi_mi': True                         
                    })

                # **Başarı mesajını logla**
                self.env['ir.logging'].sudo().create({
                    'name': 'CORDERS API Başarı',
                    'type': 'server',
                    'dbname': self._cr.dbname,
                    'level': 'info',
                    'message': f"Corders API başarılı! Yanıt: {json.dumps(result_data, indent=4)}",
                    'path': 'sale.order',
                    'line': 'action_send_to_corders',
                    'func': 'API Success'
                })

                # 📌 **Popup mesajını döndür**
                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'title': '✅ Kurye Çağrıldı!',
                        'message': "Kurye başarıyla çağrıldı ve siparişiniz işleniyor.",
                        'sticky': False,  # True yaparsan popup ekranda kalır, False ise bir süre sonra kaybolur
                        'type': 'success',  # 'success', 'warning', 'danger', 'info' olabilir
                    },
                }

                # return True  # İşlem başarılı

            else:
                _logger.error(f"❌ Corders API başarısız! Status Code: {response.status_code} - Response: {response.text}")

                self.env['ir.logging'].sudo().create({
                    'name': 'CORDERS API Hata',
                    'type': 'server',
                    'dbname': self._cr.dbname,
                    'level': 'warning',
                    "message": f"Corders API başarısız! Status Code: {response.status_code} - Response: {response.text}",
                    'path': 'sale.order',
                    'line': 'action_send_to_corders',
                    'func': 'API Error'
                })
                return False

        except Exception as e:
            _logger.error(f"🚨 Corders API bağlantı hatası: {str(e)}")

            self.env['ir.logging'].sudo().create({
                "name": "CORDERS API Bağlantı Hatası",
                "type": "server",
                "dbname": self._cr.dbname,
                "level": "error",
                "message": f"Corders API bağlantı hatası: {str(e)}",
                "path": "sale.order",
                "line": "action_send_to_corders",
                "func": "API Exception"
            })

            return False
            
        '''        

        # 📌 API'ye Sipariş Gönder
        try:
            response = session.post(f"{ODOO_URL}/web/dataset/call_kw/corders.profile/create", json=payload, headers=headers)

            if response.status_code == 200:
                
                result_data = response.json()
                _logger.info(f"Corders API yanıtı: {result_data}")
                
                # Hata olup olmadığını kontrol et
                if "error" in result_data:
                    error_message = result_data["error"].get("message", "Bilinmeyen hata")
                    _logger.error(f"Corders API Hatası: {error_message}")

                    # Hata mesajını Odoo loglarına ekle
                    self.env['ir.logging'].sudo().create({
                        'name': 'CORDERS API Hata',
                        'type': 'server',
                        'dbname': self._cr.dbname,
                        'level': 'error',
                        'message': f"Corders API başarısız! Hata: {json.dumps(result_data, indent=4)}",
                        'path': 'sale.order',
                        'line': 'action_send_to_corders',
                        'func': 'API Error'
                    })

                    # Kurye Çağrıldı butonunu aktif ETME
                    return False  # İşlemi durdur
                self.env['ir.logging'].sudo().create({
                    'name': 'CORDERS API Yanıtı',
                    'type': 'server',
                    'dbname': self._cr.dbname,
                    'level': 'info',
                    'message': f"Corders API yanıtı: {json.dumps(result_data, indent=4)}",
                    'path': 'sale.order',
                    'line': 'action_send_to_corders',
                    'func': 'API Success'
                })
                self.write({'kurye_cagrildi_mi': True})
            else:
                self.env['ir.logging'].sudo().create({
                    'name': 'CORDERS API Hata',
                    'type': 'server',
                    'dbname': self._cr.dbname,
                    'level': 'warning',
                    "message": "Corders API başarısız! Status Code: {} - Response: {}".format(response.status_code, response.text),
                    'path': 'sale.order',
                    'line': 'action_send_to_corders',
                    'func': 'API Error'
                })
        except Exception as e:
                self.env['ir.logging'].sudo().create({
                    "name": "CORDERS API Bağlantı Hatası",
                    "type": "server",
                    "dbname": self._cr.dbname,
                    "level": "error",
                    "message": f"Corders API bağlantı hatası: {str(e)}",
                    "path": "sale.order",
                    "line": "action_send_to_corders",
                    "func": "API Exception"
                })
        return True

        '''    
    def action_send_to_corders2(self):
        """
        Bu metot, butona tıklanınca Odoo'ya giriş yapar ve sipariş gönderir.
        API yanıtlarını ve hataları `ir.logging` içine kaydeder.
        """
        ODOO_URL = "https://kuryetec.autoronics.com"
        DB_NAME = "kuryetec"  # 📌 Odoo veritabanı adı
        USERNAME = "qrmenu"
        PASSWORD = "qrmenu07"

        session = requests.Session()
        
        # 1️⃣ Odoo'ya giriş yaparak session_id al
        login_payload = {
            "jsonrpc": "2.0",
            "params": {
                "login": USERNAME,
                "password": PASSWORD,
                "db": DB_NAME
            }
        }

        login_response = session.post(f"{ODOO_URL}/web/session/authenticate", json=login_payload)

        if login_response.status_code == 200:
            login_data = login_response.json()
            if login_data.get("result"):
                session_id = session.cookies.get("session_id")
                self.env['ir.logging'].sudo().create({
                    'name': 'Odoo Session Girişi',
                    'type': 'server',
                    'dbname': self._cr.dbname,
                    'level': 'info',
                    'message': f"✅ Başarıyla giriş yapıldı! Session ID: {session_id}",
                    'path': 'sale.order',
                    'line': 'action_send_to_corders',
                    'func': 'Login'
                })
            else:
                self.env['ir.logging'].sudo().create({
                    'name': 'Odoo Session Hata',
                    'type': 'server',
                    'dbname': self._cr.dbname,
                    'level': 'error',
                    'message': f"❌ Giriş başarısız: {login_data}",
                    'path': 'sale.order',
                    'line': 'action_send_to_corders',
                    'func': 'Login Error'
                })
                return False
        else:
            self.env['ir.logging'].sudo().create({
                'name': 'Odoo Session HTTP Hatası',
                'type': 'server',
                'dbname': self._cr.dbname,
                'level': 'error',
                'message': f"❌ Giriş sırasında hata oluştu: {login_response.text}",
                'path': 'sale.order',
                'line': 'action_send_to_corders',
                'func': 'Login HTTP Error'
            })
            return False

        # 2️⃣ Sipariş Verisini Hazırla
        headers = {
            "Content-Type": "application/json",
            "accept": "*/*",
            "cookie": f"session_id={session_id}"
        }
        payload = {
            "id": 30,
            "jsonrpc": "2.0",
            "method": "call",
            "params": {
                "args": [
                    {
                        "siparis_durumu": "onay_bekliyor",
                        "musteri_adi": "Test Müşterisi",
                        "musteri_telefonu": "055555555",
                        "adres": "ahatlı mah. 3000 sok. no:5 daire:4 Kepez/Antalya",
                        "siparis_notu": "sipariş notu",
                        "odeme_yontemi": "kapida_nakit",
                        "toplam_siparis_tutari": 250,
                        "magaza": 221,  # 📌 Restoran ID'si burada belirtiliyor
                        "platform": "telefon"  # 📌 Eksik alan eklendi!
                    }
                ],
                "model": "corders.profile",
                "method": "create",
                "kwargs": {
                    "context": {
                        "lang": "en_US",
                        "tz": "Turkey",
                        "uid": 2,
                        "allowed_company_ids": [1],
                        "params": {
                            "menu_id": 736,
                            "action": 1062
                        }
                    }
                }
            }
        }

        # 3️⃣ API'ye Sipariş Gönder
        try:
            response = session.post(f"{ODOO_URL}/web/dataset/call_kw/corders.profile/create", json=payload, headers=headers)

            if response.status_code == 200:
                result_data = response.json()
                self.env['ir.logging'].sudo().create({
                    'name': 'CORDERS API Yanıtı',
                    'type': 'server',
                    'dbname': self._cr.dbname,
                    'level': 'info',
                    'message': f"Corders API yanıtı: {json.dumps(result_data, indent=4)}",
                    'path': 'sale.order',
                    'line': 'action_send_to_corders',
                    'func': 'API Response'
                })
            else:
                self.env['ir.logging'].sudo().create({
                    'name': 'CORDERS API Hata',
                    'type': 'server',
                    'dbname': self._cr.dbname,
                    'level': 'warning',
                    'message': f"Corders API başarısız! Status Code: {response.status_code} - Response: {response.text}",
                    'path': 'sale.order',
                    'line': 'action_send_to_corders',
                    'func': 'API Error'
                })
        except Exception as e:
            self.env['ir.logging'].sudo().create({
                'name': 'CORDERS API Bağlantı Hatası',
                'type': 'server',
                'dbname': self._cr.dbname,
                'level': 'error',
                'message': f"Corders API bağlantı hatası: {str(e)}",
                'path': 'sale.order',
                'line': 'action_send_to_corders',
                'func': 'API Exception'
            })

        return True


'''
    
    def action_send_to_corders(self):
        """
        Butona tıklanınca Odoo'ya giriş yapıp session_id alır ve sipariş gönderir.
        """
        ODOO_URL = "https://kuryetec.autoronics.com"
        DB_NAME = "kuryetec"  # 📌 Odoo veritabanı adı
        USERNAME = "qrmenu"
        PASSWORD = "qrmenu07"

        session = requests.Session()
        
        # 1️⃣ Odoo'ya giriş yaparak session_id al
        login_payload = {
            "jsonrpc": "2.0",
            "params": {
                "login": USERNAME,
                "password": PASSWORD,
                "db": DB_NAME
            }
        }

        login_response = session.post(f"{ODOO_URL}/web/session/authenticate", json=login_payload)

        if login_response.status_code == 200:
            login_data = login_response.json()
            if login_data.get("result"):
                session_id = session.cookies.get("session_id")
                _logger.info(f"✅ Başarıyla giriş yapıldı! Session ID: {session_id}")
            else:
                _logger.error("❌ Giriş başarısız: %s", login_data)
                return False
        else:
            _logger.error("❌ Giriş sırasında hata oluştu: %s", login_response.text)
            return False

        # 2️⃣ Sipariş Verisini Hazırla
        headers = {
            "Content-Type": "application/json",
            "accept": "*/*",
            "cookie": f"session_id={session_id}"
        }

        payload = {
            "id": 30,
            "jsonrpc": "2.0",
            "method": "call",
            "params": {
                "args": [
                    {
                        "siparis_durumu": "onay_bekliyor",
                        "musteri_adi": "Test Müşterisi",
                        "musteri_telefonu": "055555555",
                        "adres": "ahatlı mah. 3000 sok. no:5 daire:4 Kepez/Antalya",
                        "siparis_notu": "sipariş notu",
                        "odeme_yontemi": "kapida_nakit",
                        "toplam_siparis_tutari": 250,
                        "magaza": 221  # 📌 Restoran ID'si burada belirtiliyor
                    }
                ],
                "model": "corders.profile",
                "method": "create",
                "kwargs": {
                    "context": {
                        "lang": "en_US",
                        "tz": "Turkey",
                        "uid": 2,
                        "allowed_company_ids": [1],
                        "params": {
                            "menu_id": 736,
                            "action": 1062
                        }
                    }
                }
            }
        }

        # 3️⃣ API'ye Sipariş Gönder
        response = session.post(f"{ODOO_URL}/web/dataset/call_kw/corders.profile/create", json=payload, headers=headers)

        if response.status_code == 200:
            _logger.info("✅ Sipariş başarıyla oluşturuldu: %s", response.json())
        else:
            _logger.error("❌ Sipariş oluşturulamadı: %s", response.text)

        return True
'''



'''
    
    def action_send_to_corders(self):
        
        """
        Bu metot, butona basılınca kuryetec.autoronics.com'a POST isteği atar ve sonucu ir.logging'e yazar.
        """
        url = "https://kuryetec.autoronics.com/web/dataset/call_kw/corders.profile/create"

        headers = {
            "Content-Type": "application/json",
            "accept": "*/*",
        }

        payload = {
            "id": 30,
            "jsonrpc": "2.0",
            "method": "call",
            "params": {
                "args": [
                    {
                        "siparis_durumu": "onay_bekliyor",
                        "musteri_adi": "Test Müşterisi",
                        "musteri_telefonu": "055555555",
                        "adres": "ahatlı mah. 3000 sok. no:5 daire:4 Kepez/Antalya",
                        "siparis_notu": "sipariş notu",
                        "odeme_yontemi": "kapida_nakit",
                        "toplam_siparis_tutari": 250,
                    }
                ],
                "model": "corders.profile",
                "method": "create",
                "kwargs": {
                    "context": {
                        "lang": "en_US",
                        "tz": "Turkey",
                        "uid": 2,
                        "allowed_company_ids": [1],
                        "params": {
                            "menu_id": 736,
                            "action": 1062
                        }
                    }
                }
            }
        }

        try:
            # Log kaydını ir.logging'e yazdırıyoruz
            self.env['ir.logging'].sudo().create({
                'name': 'CORDERS API İsteği',
                'type': 'server',
                'dbname': self._cr.dbname,
                'level': 'info',
                'message': f"Corders API'ye gönderilen veri: {json.dumps(payload, indent=4)}",
                'path': 'sale.order',
                'line': 'action_send_to_corders',
                'func': 'POST Request'
            })
            
            response = requests.post(url, data=json.dumps(payload), headers=headers, timeout=15)

            if response.status_code == 200:
                result_data = response.json()
                self.env['ir.logging'].sudo().create({
                    'name': 'CORDERS API Yanıtı',
                    'type': 'server',
                    'dbname': self._cr.dbname,
                    'level': 'info',
                    'message': f"Corders API yanıtı: {json.dumps(result_data, indent=4)}",
                    'path': 'sale.order',
                    'line': 'action_send_to_corders',
                    'func': 'POST Response'
                })
                self.message_post(body=f"Corders API'ye başarıyla gönderildi. Yanıt: {result_data}")
            else:
                self.env['ir.logging'].sudo().create({
                    'name': 'CORDERS API Hata',
                    'type': 'server',
                    'dbname': self._cr.dbname,
                    'level': 'warning',
                    'message': f"Corders API başarısız! Status Code: {response.status_code} - Response: {response.text}",
                    'path': 'sale.order',
                    'line': 'action_send_to_corders',
                    'func': 'POST Error'
                })
                self.message_post(body=f"Corders API başarısız. Status Code: {response.status_code}")

        except Exception as e:
            self.env['ir.logging'].sudo().create({
                'name': 'CORDERS API Bağlantı Hatası',
                'type': 'server',
                'dbname': self._cr.dbname,
                'level': 'error',
                'message': f"Corders API bağlantı hatası: {str(e)}",
                'path': 'sale.order',
                'line': 'action_send_to_corders',
                'func': 'POST Exception'
            })
            self.message_post(body=f"Corders API bağlantı hatası: {str(e)}")

        return True


'''



'''
    
    
                              
def action_send_to_corders(self):
        """
        Bu metot, butona basılınca kuryetec.autoronics.com'a POST isteği atar.
        """
        # 1) Gönderilecek URL
        url = "https://kuryetec.autoronics.com/web/dataset/call_kw/corders.profile/create"
        
        # 2) Header bilgisi
        headers = {
            "Content-Type": "application/json",
            "accept": "*/*",
            # Burada gerekiyorsa ekstra header ekleyebilirsiniz
            # "cookie": "...", 
            # "Authorization": "Bearer xxx",
        }

        # 3) POST edilecek veri (payload)
        # Postman örneğinizde "body" içinde yer alan JSON’u Python dict olarak oluşturuyoruz.
        # Aşağıdakini örnek olarak yazıyorum, siz kendi ihtiyacınıza göre düzenleyin:
        payload = {
            "id": 30,
            "jsonrpc": "2.0",
            "method": "call",
            "params": {
                "args": [
                    {
                        "siparis_durumu": "onay_bekliyor",
                        "musteri_adi": "Test Müşterisi",
                        "musteri_telefonu": "055555555",
                        "adres": "ahatlı mah. 3000 sok. no:5 daire:4 Kepez/Antalya",
                        "adres_tarifi": "adres tarifi",
                        "siparis_notu": "sipariş notu",
                        "odeme_yontemi": "kapida_nakit",
                        "toplam_siparis_tutari": 250,
                        # ... Postman'daki diğer alanlar ...
                        "order_profile_lines": [
                            [0, "virtual_4", {
                                "order_sequence": 0,
                                "urun": "Test Ürünü",
                                # ...
                            }]
                        ],
                    }
                ],
                "model": "corders.profile",
                "method": "create",
                "kwargs": {
                    "context": {
                        "lang": "en_US",
                        "tz": "Turkey",
                        "uid": 2,
                        "allowed_company_ids": [1],
                        "params": {
                            "menu_id": 736,
                            "action": 1062
                        }
                    }
                }
            }
        }
        
        # 4) İsteği gönder
        try:
            response = requests.post(url, data=json.dumps(payload), headers=headers, timeout=15)
            # timeout ile 15 saniye içinde yanıt gelmezse hata alırız

            if response.status_code == 200:
                # Başarılı isteğe göre işlem
                # response.json() ile JSON parse edebilirsiniz
                result_data = response.json()
                # Örnek: self.message_post(body=f"İşlem başarılı: {result_data}")
            else:
                # Hata durumları
                # Örnek: self.message_post(body=f"İstek başarısız: {response.status_code} - {response.text}")
                pass
        except Exception as e:
            # İstek sırasında bağlantı hatası vb. olursa
            # self.message_post(body=f"İstek hatası: {str(e)}")
            pass
        
        return True
'''