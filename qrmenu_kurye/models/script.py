from odoo import tools, fields, models, api, _
from odoo.exceptions import UserError
import requests
import json
import logging

_logger = logging.getLogger(__name__)

class SaleOrderInherit(models.Model):
    _inherit = 'sale.order'

    # 🛠️ Yeni Alanlar (Odoo'dan çekilecek veriler için)
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
    odeme_yontemi = fields.Selection([
        ('kapida_nakit', 'Kapıda Nakit'),
        ('kapida_kredi', 'Kapıda Kredi Kartı'),
        ('havale', 'Havale')
    ], default='kapida_nakit', string="Ödeme Yöntemi")

    toplam_siparis_tutari = fields.Float(string="Toplam Sipariş Tutarı")
    platform = fields.Selection([
        ('telefon', 'Telefon'),
        ('web', 'Web'),
        ('mobil', 'Mobil Uygulama')
    ], default='telefon', string="Platform")
    
    magaza = fields.Many2one('res.partner', string="Mağaza")  # Mağaza ID

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
                        "magaza": self.magaza.id if self.magaza else 221,  # Eğer mağaza seçilmemişse 221 olarak gönder
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
