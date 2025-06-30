from odoo import tools, fields, models, api,_
from odoo.exceptions import UserError
from odoo.exceptions import ValidationError
import requests
import json
import logging
from datetime import datetime
from base64 import b64encode
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
    

class SaleOrderInherit(models.Model):
    
    
    _inherit = 'sale.order'
    
    siparis_durumu = fields.Selection([
        ('onay_bekliyor', 'Onay Bekliyor'),
        ('hazırlanıyor', 'Hazırlanıyor'),
        ('teslim_edildi', 'Teslim Edildi')
    ], default='onay_bekliyor', string="Sipariş Durumu")

    musteri_adi = fields.Char(string="Müşteri Adı")
    musteri_telefonu = fields.Char(string="Müşteri Telefonu")
    adres = fields.Text(string="Adres")
    adres_tarifi = fields.Text(string="Adres Tarifi")
    siparis_notu = fields.Text(string="Sipariş Notu")
    odeme_yontemi = fields.Selection([('kapida_nakit','Kapıda Nakit Ödeme'),('kapida_kredi_karti','Kapıda Kredi Kartı'),('online_odendi','Online Ödendi'),('uygulamadan_odendi','Uygulamadan Ödendi')],
                                    string="Ödeme Yöntemi", tracking=True
                                    )


    toplam_siparis_tutari = fields.Float(string="Toplam Sipariş Tutarı")
    platform = fields.Selection([
        ('telefon', 'Telefon'),
        ('web', 'Web'),
        ('mobil', 'Mobil Uygulama')
    ], default='telefon', string="Platform")
    
    magaza = fields.Many2one('res.partner', string="Mağaza")  # Mağaza ID
    restaurant_id = fields.Integer(string="Restoran ID", help="Restoranın ID bilgisini manuel olarak gireceksiniz.")
    
    
    def action_send_to_corders(self):
        """
        📌 Butona tıklanınca API'ye sipariş gönderir. Log kayıtlarını ir.logging içine ekler.
        """
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
                self.env['ir.logging'].create({
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
                self.env['ir.logging'].create({
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
            self.env['ir.logging'].create({
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
                        #"magaza": self.magaza.id if self.magaza else 221,  # Eğer mağaza seçilmemişse 221 olarak gönder
                        "magaza": self.restaurant_id,  # Eğer mağaza seçilmemişse 221 olarak gönder
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
                self.env['ir.logging'].create({
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
                self.env['ir.logging'].create({
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
            self.env['ir.logging'].create({
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
                self.env['ir.logging'].create({
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
                self.env['ir.logging'].create({
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
            self.env['ir.logging'].create({
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
                self.env['ir.logging'].create({
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
                self.env['ir.logging'].create({
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
            self.env['ir.logging'].create({
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
            self.env['ir.logging'].create({
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
                self.env['ir.logging'].create({
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
                self.env['ir.logging'].create({
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
            self.env['ir.logging'].create({
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