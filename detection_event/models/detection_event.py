from odoo import tools, fields, models, api,_
from odoo.exceptions import UserError
from odoo.exceptions import ValidationError
import requests
import json
from datetime import datetime
from base64 import b64encode
 

cookie = "detection_event"
import logging
_logger = logging.getLogger(__name__)

class DetectionEvent(models.Model):
    _name = "detection_event.profile"     
    _description = 'Gerçek Zamanlı Algılama Olayı'

    sequence = fields.Integer(string="Sequence")


    # Temel bilgiler
    name = fields.Char(string="Olay Başlığı",  default="Yeni Olay")
    event_type = fields.Selection([
        ('person', 'İnsan Algılandı'),
        ('vehicle', 'Araç Algılandı'),
        ('unauthorized', 'İzinsiz Giriş'),
        ('other', 'Diğer')],
        string="Olay Türü",  default='other')
    
    description = fields.Text(string="Açıklama")
    timestamp = fields.Datetime(string="Zaman", default=lambda self: fields.Datetime.now())
    
    severity = fields.Selection([
        ('info', 'Bilgi'),
        ('warning', 'Uyarı'),
        ('critical', 'Kritik')],
        string="Öncelik", default='info' )
    
    image_url = fields.Char(string="Görüntü URL'si")

    # Onay bilgileri
    acknowledged = fields.Boolean(string="Onaylandı", default=False)
    ack_date = fields.Datetime(string="Onay Zamanı")
    ack_user_id = fields.Many2one('res.users', string="Onaylayan")
    ack_comment = fields.Text(string="Kullanıcı Yorumu")

    # Response bilgileri
    response_status = fields.Selection([
        ('acknowledged', 'Gördüm ve Onaylıyorum'),
        ('in_progress', 'İnceleniyor'),
        ('resolved', 'Çözüldü'),
        ('false_alarm', 'Yanlış Alarm')],
        string="Durum", default='acknowledged')
    
    protocols_followed = fields.Text(string="Uygulanan Protokoller")



    # yeni eklenen field
    device_name = fields.Char(string="Device Name")
    ademco_id = fields.Char(string="Ademco ID")
    zone = fields.Integer(string="Zone")    
    event_date = fields.Datetime(string="Olay Zamanı")
    
    
    def _notify_refresh(self):
        # 3 parametre: kanal, mesaj tipi, veri
        self.env['bus.bus'].sudo()._sendone(
            'broadcast',                # tüm istemcilere yayın
            'detection_event_update',   # istediğiniz benzersiz mesaj tipi
            {'model_name': self._name}
        )

    @api.model
    def create(self, vals):
        record = super().create(vals)
        record._notify_refresh()
        return record

    def write(self, vals):
        res = super().write(vals)
        self._notify_refresh()
        return res



    