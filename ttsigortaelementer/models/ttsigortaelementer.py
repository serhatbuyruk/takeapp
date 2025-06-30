from odoo import tools, fields, models, api,_
from odoo.exceptions import UserError
from odoo.exceptions import ValidationError
import requests
import json
from datetime import datetime
from base64 import b64encode

 

cookie = "ttsigortaelementer"
import logging
_logger = logging.getLogger(__name__)

class ttsigortaelementer(models.Model):
    
    _name = "ttsigortaelementer.profile"
    _description = "TT Sigorta Elementer"

    name = fields.Char(string="Name", required=True)
    description = fields.Char(string="Description")
    sequence = fields.Integer(string="Sequence", default=1)

    
    elementer_selection = fields.Selection(
        [
            ('oto', 'Araç Sigortaları'),
            ('konut', 'Konut'),
            ('isyeri', 'İşyeri Sigortası')
        ],
        string="Elementer Sigortalar",
        default=""
    )

    # Elementer

    # Araç Sigortaları
    ruhsat = fields.Char(string="Ruhsat")
    phone = fields.Char(string="Telefon")
    plaka = fields.Char(string="Plaka")
    seri_no = fields.Char(string="Seri No")
    marka = fields.Char(string="Marka")
    model = fields.Char(string="Model")

    # Konut
    konutselection = fields.Selection(
        [
            ('dask', 'Dask'),
            ('sbinasigortasi', 'Sadece Bina Sigortası'),
            ('sesyasigortasi', 'Sadece Eşya Sigortası'),
            ('konutpaketsigortasi', 'Konut Paket Sigortası(Herşe dahil pakit)')
        ],
        string="Konut Sigortalar",
        default=""
    )

    # Dask -- Bina

    dask_tc = fields.Char(string="Bina Sahibi TC kimlik")
    dask_adress = fields.Char(string="Açık adress(UluslararasıAVT)")
    dask_daire_metrekare = fields.Char(string="Daire Metre Karesi")
    dask_bina_yas = fields.Integer(string="Bina Yaşı")
    dask_bina_kat_adet = fields.Integer(string="Binan toplam kat adeti")
    dask_bina_kat = fields.Integer(string="Daire Kaçıncı Katta Olduğu")

    # Bina

    bina_tc = fields.Char(string="Bina Sahibi TC kimlik")
    bina_adress = fields.Char(string="Açık adress(UluslararasıAVT)")
    bina_daire_metrekare = fields.Char(string="Daire Metre Karesi")
    bina_yas = fields.Integer(string="Bina Yaşı")
    bina_kat_adet = fields.Integer(string="Binan toplam kat adeti")
    bina_kat = fields.Integer(string="Daire Kaçıncı Katta Olduğu")




    # Eşya

    esya_tc = fields.Char(string="Bina Sahibi TC kimlik")
    esya_adress = fields.Char(string="Açık adress(UluslararasıAVT)")
    esya_daire_metrekare = fields.Char(string="Daire Metre Karesi")
    esya_bina_yas = fields.Integer(string="Bina Yaşı")
    esya_bina_kat_adet = fields.Integer(string="Binan toplam kat adeti")
    esya_bina_kat = fields.Integer(string="Daire Kaçıncı Katta Olduğu")
    esya_raic_bedel = fields.Float(string="Raiç Eşya bedeli")

    # Konut paket sigortası(Herşe dahil pakit)

    paket_tc = fields.Char(string="Bina Sahibi TC kimlik")
    paket_adress = fields.Char(string="Açık adress(UluslararasıAVT)")
    paket_daire_metrekare = fields.Char(string="Daire Metre Karesi")
    paket_bina_yas = fields.Integer(string="Bina Yaşı")
    paket_bina_kat_adet = fields.Integer(string="Binan toplam kat adeti")
    paket_bina_kat = fields.Integer(string="Daire Kaçıncı Katta Olduğu")
    paket_raic_bedel = fields.Float(string="Raiç Eşya bedeli")


    # İş Yeri Sigortası -konut paket sigortası(Herşe dahil pakit)

    is_tc = fields.Char(string="Bina Sahibi TC kimlik")
    is_adress = fields.Char(string="Açık adress(UluslararasıAVT)")
    is_daire_metrekare = fields.Char(string="Daire Metre Karesi")
    is_bina_yas = fields.Integer(string="Bina Yaşı")
    is_bina_kat_adet = fields.Integer(string="Binan toplam kat adeti")
    is_bina_kat = fields.Integer(string="Daire Kaçıncı Katta Olduğu")
    is_raic_bedel = fields.Float(string="Raiç Eşya bedeli")
    is_kira_mal_sahibi = fields.Selection(
        [
            ('kira', 'Kira'),           
            ('malsahibi', ' Mal sahibi')
        ],
        string="Kira mı Mal sahibi",
        default=""
    )
    is_ne_is_yapiyor = fields.Char(string="Ne iş yapıyor")
    is_satmak_istedigi_mal = fields.Char(string="Var ise satmaya sunduğu emtiya mal bedeli")
    is_demirbas_bedeli = fields.Float(string="Demirbaş Bedeli")
    is_guvenlik_onlemleri = fields.Char(string="Güvenlik Önlemleri")
    is_yangin_onlemleri = fields.Char(string="Yangın Önlemleri")
    is_calisan_sayisi = fields.Integer(string="Çalışan Sayısı")







    """ dask = fields.Char(string="Dask")
    sbinasigortasi = fields.Char(string="Sadece Bina Sigortası")
    sesyasigortasi = fields.Char(string="Sadece Eşya Sigortası")
    konutpaketsigortasi = fields.Char(string="konut Paket Sigortası(Herşe dahil pakit)") """


    
    






    


 

