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
    

    # Yeni Eklenen Kısımlar burası
    code = fields.Char(string="Order Code")
    customer_name = fields.Char(string="Customer Name")
    customer_phone = fields.Char(string="Customer Phone")
    order_status = fields.Selection([
        ('created', 'Created'),
        ('accepted', 'Accepted'),
        ('prepared', 'Prepared'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled')
    ], string="Order Status", default='created')
    total_price = fields.Float(string="Total Price")
    payment_status = fields.Selection([
        ('paid', 'Paid'),
        ('pending', 'Pending')
    ], string="Payment Status")
    
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
                
        _logger.info("✅ action_send_to_corders metodu çalıştı!")

        # Eğer kurye zaten çağrıldıysa işlemi durdur
        if self.kurye_cagrildi_mi:
            _logger.warning("❌ Kurye zaten çağrıldı, tekrar çağrılamaz!")
            raise UserError(_("Kurye zaten çağrıldı, tekrar çağrılamaz!"))

        # Restoran ID kontrolü
        if not self.restaurant_id:
            raise UserError(_("Restoran ID eksik! Lütfen restoran ID seçin."))

        # Ödeme yöntemi kontrolü
        if not self.odeme_yontemi:
            raise UserError(_("Ödeme yöntemi seçilmedi! Sipariş gönderilemez."))

        # **Market ID ve Token**
        MARKET_ID = "1"
        TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6MjB9.MinKwO0ex1GyT3a8kJ6cyC8elhHhZ9SnxxGG6Asj4no"

        # API URL ve Kimlik Doğrulama Bilgileri
        url = "https://possiweb.com/api/v1/webhook/possi-food/order/dinamik_qr"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {TOKEN}"
        }

        # Sipariş Verisini API formatına dönüştürme
        payload = {
            "market_id": MARKET_ID,  # Buraya market_id eklendi
            "code": self.code or f"SO-{self.id}",
            "comment": {
                "message": self.siparis_notu or "Sipariş notu yok."
            },
            "customer": {
                "code": str(self.partner_id.id),
                "email": self.partner_id.email or "",
                "first_name": self.partner_id.name.split()[0] if self.partner_id.name else "",
                "id": str(self.partner_id.id),
                "last_name": " ".join(self.partner_id.name.split()[1:]) if len(self.partner_id.name.split()) > 1 else "",
                "phone": self.partner_id.phone or self.partner_id.mobile or ""
            },
            "delivery": {
                "address": {
                    "building": "",
                    "city": self.partner_id.city or "",
                    "company": self.partner_id.parent_id.name if self.partner_id.parent_id else "",
                    "delivery_area": "",
                    "delivery_instructions": self.adres_tarifi or "",
                    "delivery_main_area": "",
                    "entrance": "",
                    "flat_number": "",
                    "floor": "",
                    "intercom": "",
                    "latitude": 0.0,
                    "longitude": 0.0,
                    "number": "",
                    "post_code": "",
                    "street": self.partner_id.street or ""
                },
                "expected_delivery_time": "2024-09-18T18:22:15.000Z"  # Örnek tarih
            },
            "expedition_type": "delivery",
            "order_statuses": [{"message": "Sipariş oluşturuldu", "status": "created"}],
            "payment": {
                "remote_code": self.odeme_yontemi,
                "status": "paid" if self.payment_status == "paid" else "pending",
                "type": self.odeme_yontemi
            },
            "price": {
                "grand_total": self.amount_total,
                "total_net": self.amount_total * 0.82,  # Örnek KDV hesaplama
                "vat_total": self.amount_total * 0.18  # Örnek KDV hesaplama
            },
            "products": [{
                "category_name": line.product_id.categ_id.name,
                "comment": "",
                "description": line.product_id.name,
                "discount_amount": 0,
                "id": str(line.product_id.id),
                "name": line.product_id.name,
                "paid_price": line.price_total,
                "quantity": line.product_uom_qty,
                "remote_code": str(line.product_id.id),
                "unit_price": line.price_unit,
                "selected_toppings": []
            } for line in self.order_line],
            "remote_created_at": fields.Datetime.now().isoformat(),
            "short_code": str(self.id),
            "token": TOKEN  # API'ye ekstra güvenlik için token ekledik
        }

        # API'ye POST isteği gönderme
        try:
            response = requests.post(url, headers=headers, json=payload)
            response_data = response.json()

            if response.status_code == 200:
                _logger.info("✅ Sipariş başarıyla gönderildi!")
                self.kurye_cagrildi_mi = True
                return {
                    'effect': {
                        'fadeout': 'slow',
                        'message': 'Kurye çağrıldı!',
                        'type': 'rainbow_man',
                    }
                }
            else:
                _logger.error(f"❌ Sipariş gönderilemedi! Hata: {response_data}")
                raise UserError(_("Sipariş gönderilemedi! Hata: %s") % response_data)

        except requests.exceptions.RequestException as e:
            _logger.error(f"🚨 API bağlantı hatası: {str(e)}")
            raise UserError(_("🚨 API bağlantı hatası: %s") % str(e))
    




    def action_send_to_corders3(self):
        
        _logger.info("✅ action_send_to_corders metodu çalıştı!")

        # Eğer kurye zaten çağrıldıysa işlemi durdur
        if self.kurye_cagrildi_mi:
            _logger.warning("❌ Kurye zaten çağrıldı, tekrar çağrılamaz!")
            raise UserError(_("Kurye zaten çağrıldı, tekrar çağrılamaz!"))

        # Restoran ID kontrolü
        if not self.restaurant_id:
            raise UserError(_("Restoran ID eksik! Lütfen restoran ID seçin."))

        # Ödeme yöntemi kontrolü
        if not self.odeme_yontemi:
            raise UserError(_("Ödeme yöntemi seçilmedi! Sipariş gönderilemez."))

        # API URL ve Kimlik Doğrulama Bilgileri
        url = "https://possiweb.com/api/v1/webhook/possi-food/order/dinamik_qr"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6MjB9.MinKwO0ex1GyT3a8kJ6cyC8elhHhZ9SnxxGG6Asj4no"
        }

        # Sipariş Verisini API formatına dönüştürme
        payload = {
            "code": self.code or f"SO-{self.id}",
            "comment": {
                "message": self.siparis_notu or "Sipariş notu yok."
            },
            "customer": {
                "code": str(self.partner_id.id),
                "email": self.partner_id.email or "",
                "first_name": self.partner_id.name.split()[0] if self.partner_id.name else "",
                "id": str(self.partner_id.id),
                "last_name": " ".join(self.partner_id.name.split()[1:]) if len(self.partner_id.name.split()) > 1 else "",
                "phone": self.partner_id.phone or self.partner_id.mobile or ""
            },
            "delivery": {
                "address": {
                    "building": "",
                    "city": self.partner_id.city or "",
                    "company": self.partner_id.parent_id.name if self.partner_id.parent_id else "",
                    "delivery_area": "",
                    "delivery_instructions": self.adres_tarifi or "",
                    "delivery_main_area": "",
                    "entrance": "",
                    "flat_number": "",
                    "floor": "",
                    "intercom": "",
                    "latitude": 0.0,
                    "longitude": 0.0,
                    "number": "",
                    "post_code": "",
                    "street": self.partner_id.street or ""
                },
                "expected_delivery_time": "2024-09-18T18:22:15.000Z"  # Örnek tarih
            },
            "market_code": "1",  # Sabit market ID (Özel bir ID varsa değiştir)
            "expedition_type": "delivery",
            "order_statuses": [{"message": "Sipariş oluşturuldu", "status": "created"}],
            "payment": {
                "remote_code": self.odeme_yontemi,
                "status": "paid" if self.payment_status == "paid" else "pending",
                "type": self.odeme_yontemi
            },
            "price": {
                "grand_total": self.amount_total,
                "total_net": self.amount_total * 0.82,  # Örnek KDV hesaplama
                "vat_total": self.amount_total * 0.18  # Örnek KDV hesaplama
            },
            "products": [{
                "category_name": line.product_id.categ_id.name,
                "comment": "",
                "description": line.product_id.name,
                "discount_amount": 0,
                "id": str(line.product_id.id),
                "name": line.product_id.name,
                "paid_price": line.price_total,
                "quantity": line.product_uom_qty,
                "remote_code": str(line.product_id.id),
                "unit_price": line.price_unit,
                "selected_toppings": []
            } for line in self.order_line],
            "remote_created_at": fields.Datetime.now().isoformat(),
            "short_code": str(self.id),
            "token": "random_generated_token"
        }

        # API'ye POST isteği gönderme
        try:
            response = requests.post(url, headers=headers, json=payload)
            response_data = response.json()

            if response.status_code == 200:
                _logger.info("✅ Sipariş başarıyla gönderildi!")
                self.kurye_cagrildi_mi = True
                return {
                    'effect': {
                        'fadeout': 'slow',
                        'message': 'Kurye çağrıldı!',
                        'type': 'rainbow_man',
                    }
                }
            else:
                _logger.error(f"❌ Sipariş gönderilemedi! Hata: {response_data}")
                raise UserError(_("Sipariş gönderilemedi! Hata: %s") % response_data)

        except requests.exceptions.RequestException as e:
            _logger.error(f"🚨 API bağlantı hatası: {str(e)}")
            raise UserError(_("🚨 API bağlantı hatası: %s") % str(e))



    def action_send_to_corders2(self):
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

       
        
        