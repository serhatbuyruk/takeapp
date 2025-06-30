from odoo import tools, fields, models, api, _
from odoo.exceptions import UserError, ValidationError
import requests
import logging
import hashlib
import base64

_logger = logging.getLogger(__name__)

class ParamProfile(models.Model):
    _name = "param.profile"
    _description = "Param Profile"

    name = fields.Char(string="Name")
    sequence = fields.Integer(string="Sequence", default=1)
    banka = fields.Char(string="Banka Adı")
    Kart_No = fields.Char(string="Kart No")
    KK_Sahibi = fields.Char(string="Kredi Kart Sahibi")
    KK_No = fields.Char(string="Kredi Kart No")
    KK_SK_Ay = fields.Char(string="Ay")
    KK_SK_Yil = fields.Char(string="Yıl")
    KK_CVV = fields.Char(string="CVV")
    Data1 = fields.Char(string="Data1")
    Data2 = fields.Char(string="Data2")
    Data3 = fields.Char(string="Data3")

    @api.model
    def stws_guvenlik(self, CLIENT_CODE, CLIENT_USERNAME, CLIENT_PASSWORD, Kart_No, KK_Sahibi, KK_No, KK_SK_Ay, KK_SK_Yil, KK_CVV):
        url = "https://test-dmz.param.com.tr/turkpos.ws/service_turkpos_test.asmx"
        # SOAP isteği
        payload = f"""<?xml version="1.0" encoding="utf-8"?>
<soap:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
  <soap:Body>
    <KK_Saklama xmlns="https://turkpos.com.tr/">
      <G>
        <CLIENT_CODE>{CLIENT_CODE}</CLIENT_CODE>
        <CLIENT_USERNAME>{CLIENT_USERNAME}</CLIENT_USERNAME>
        <CLIENT_PASSWORD>{CLIENT_PASSWORD}</CLIENT_PASSWORD>
      </G>
      <Kart_No>{Kart_No}</Kart_No>
      <KK_Sahibi>{KK_Sahibi}</KK_Sahibi>
      <KK_No>{KK_No}</KK_No>
      <KK_SK_Ay>{KK_SK_Ay}</KK_SK_Ay>
      <KK_SK_Yil>{KK_SK_Yil}</KK_SK_Yil>
      <KK_CVV>{KK_CVV}</KK_CVV>
      <Data1>string</Data1>
      <Data2>string</Data2>
      <Data3>string</Data3>
    </KK_Saklama>
  </soap:Body>
</soap:Envelope>
"""

        # HTTP başlıkları
        headers = {
            'Content-Type': 'text/xml; charset=utf-8',
            'SOAPAction': '"https://turkpos.com.tr/KK_Saklama"'
        }

        # POST isteği gönderme
        # response = requests.post(url, data=payload.encode('utf-8'), headers=headers)

        # Yanıtın durum kodunu ve içeriğini yazdırma
        # return("Response Content:", response.content.decode('utf-8'))
        
        try:                       
            response = requests.post(url, data=payload.encode('utf-8'), headers=headers)
            response.raise_for_status()  # Raise an error for bad responses
        except requests.exceptions.HTTPError as errh:
            _logger.error("HTTP Error: %s", errh)
            raise UserError(_("HTTP Error: %s") % errh)
        except requests.exceptions.ConnectionError as errc:
            _logger.error("Error Connecting: %s", errc)
            raise UserError(_("Error Connecting: %s") % errc)
        except requests.exceptions.Timeout as errt:
            _logger.error("Timeout Error: %s", errt)
            raise UserError(_("Timeout Error: %s") % errt)
        except requests.exceptions.RequestException as err:
            _logger.error("Error: %s", err)
            raise UserError(_("Error: %s") % err)

        # Return response content
        return response.content.decode('utf-8')
