# -*- coding: utf-8 -*-
from odoo import api, fields, models, tools
from odoo import http
from odoo.http import request, Response
from datetime import datetime
import logging
import requests
import json
_logger = logging.getLogger(__name__)
from odoo.tools import date_utils
import base64


class EtkinPromosyonController(http.Controller):
    
    # https://kreatifcozumler.com/api/kategoriler
    @http.route('/api/kategoriler', type='http', auth='public', methods=['GET'], website=True)
    def kategoriler(self):
        """
        Tüm kategorileri listelemek için API çağrısı.
        """
        url = "http://www.birikimpromosyon.com/api/json/"
        payload = {
            "ebayi_eposta": "info@kreatifcozumler.com",
            "hash": "892cfb16ebbdbdd8abb3630810a0792f",
            "tip": "tum_kategoriler"
        }
        headers = {
            "Content-Type": "application/json",
            "User-Agent": "kreatifcozumler.com",
        }

        try:
            response = requests.post(url, headers=headers, data=json.dumps(payload), timeout=20)
            response.raise_for_status()
            data = response.json()
        except requests.exceptions.RequestException as e:
            data = {"error": str(e)}

        return request.make_response(
            json.dumps(data),
            headers={'Content-Type': 'application/json'}
        )

    # https://www.kreatifcozumler.com/en/api/urunler?kategori_id=13
    @http.route('/api/urunler', type='http', auth='public', methods=['GET'], website=True)
    def urunler(self, kategori_id=None):
        """
        Belirli bir kategoriye bağlı ürünleri listelemek için API çağrısı.
        """
        if not kategori_id:
            return request.make_response(
                json.dumps({"error": "Kategori ID eksik!"}),
                headers={'Content-Type': 'application/json'}
            )

        url = "http://www.birikimpromosyon.com/api/json/"
        payload = {
            "ebayi_eposta": "info@kreatifcozumler.com",
            "hash": "892cfb16ebbdbdd8abb3630810a0792f",
            "tip": "array_kategori_urunler",
            "array_kategoriler": [int(kategori_id)]
        }
        headers = {
            "Content-Type": "application/json",
            "User-Agent": "kreatifcozumler.com",
        }

        try:
            response = requests.post(url, headers=headers, data=json.dumps(payload), timeout=20)
            response.raise_for_status()
            data = response.json()
        except requests.exceptions.RequestException as e:
            data = {"error": str(e)}

        return request.make_response(
            json.dumps(data),
            headers={'Content-Type': 'application/json'}
        )
        
    
    # https://kreatifcozumler.com/api/varyant/urunler?kategori_id=13 
    @http.route('/api/varyant/urunler', type='http', auth='public', methods=['GET'], website=True)
    def varyant_urunler(self, kategori_id=None): 
        if not kategori_id:
            return request.make_response(
                json.dumps({"error": "Kategori ID eksik!"}),
                headers={'Content-Type': 'application/json'}
            )

        url = "http://www.birikimpromosyon.com/api/json/"
        payload = {
            "ebayi_eposta": "info@kreatifcozumler.com",
            "hash": "892cfb16ebbdbdd8abb3630810a0792f",
            "tip": "array_varyant_kategori_urunler",
            "array_kategoriler": [int(kategori_id)]
        }
        headers = {
            "Content-Type": "application/json",
            "User-Agent": "kreatifcozumler.com",
        }

        try:
            response = requests.post(url, headers=headers, data=json.dumps(payload), timeout=20)
            response.raise_for_status()
            data = response.json()
        except requests.exceptions.RequestException as e:
            data = {"error": str(e)}

        return request.make_response(
            json.dumps(data),
            headers={'Content-Type': 'application/json'}
        )   
     
    # https://kreatifcozumler.com/api/varyant/urunler/detay?kategori_id=13&urun_id=17687 
    @http.route('/api/varyant/urunler/detay', type='http', auth='public', methods=['GET'], website=True)
    def varyant_urunler_detay(self, kategori_id=None, urun_id=None):
        """
        Kategori ID ve opsiyonel olarak Ürün ID'ye göre ürünleri listeleme.
        Eğer `urun_id` verilirse, yalnızca o ürünü döndürür.
        """
        if not kategori_id:
            return request.make_response(
                json.dumps({"error": "Kategori ID eksik!"}),
                headers={'Content-Type': 'application/json'}
            )

        url = "http://www.birikimpromosyon.com/api/json/"
        payload = {
            "ebayi_eposta": "info@kreatifcozumler.com",
            "hash": "892cfb16ebbdbdd8abb3630810a0792f",
            "tip": "array_varyant_kategori_urunler",
            "array_kategoriler": [int(kategori_id)]
        }

        headers = {
            "Content-Type": "application/json",
            "User-Agent": "kreatifcozumler.com",
        }

        try:
            # API Çağrısı
            response = requests.post(url, headers=headers, data=json.dumps(payload), timeout=20)
            response.raise_for_status()
            data = response.json()

            # Eğer urun_id verilmişse, sadece o ürünü döndür
            if urun_id:
                filtered_product = next((urun for urun in data if str(urun.get("urun_id")) == urun_id), None)
                if not filtered_product:
                    return request.make_response(
                        json.dumps({"error": f"Ürün ID {urun_id} bulunamadı!"}),
                        headers={'Content-Type': 'application/json'}
                    )
                return request.make_response(
                    json.dumps(filtered_product, indent=4, ensure_ascii=False),
                    headers={'Content-Type': 'application/json'}
                )

            # Eğer sadece kategori_id varsa, tüm ürünleri döndür
            return request.make_response(
                json.dumps(data, indent=4, ensure_ascii=False),
                headers={'Content-Type': 'application/json'}
            )

        except requests.exceptions.RequestException as e:
            return request.make_response(
                json.dumps({"error": str(e)}),
                headers={'Content-Type': 'application/json'}
            )
            
        

    @http.route('/turuncu/kategoriler', type='http', auth='public', website=True)
    def kategoriler_html(self):
        url = "http://www.birikimpromosyon.com/api/json/"
        payload = {
            "ebayi_eposta": "info@kreatifcozumler.com",
            "hash": "892cfb16ebbdbdd8abb3630810a0792f",
            "tip": "tum_kategoriler"
        }
        headers = {
            "Content-Type": "application/json",
            "User-Agent": "kreatifcozumler.com",
        }

        try:
            response = requests.post(url, headers=headers, data=json.dumps(payload), timeout=20)
            response.raise_for_status()
            data = response.json()

            # Eğer gelen veri liste ise, sözlüğe dönüştür
            if isinstance(data, list):
                data = {"data": data}

        except requests.exceptions.RequestException as e:
            data = {"error": str(e)}

        return request.render('kreatif.etkin_promosyon_kategoriler_page', {'data': data})

    # https://www.kreatifcozumler.com/en/turuncu/urunler?kategori_id=13
    @http.route('/turuncu/urunler', type='http', auth='public', website=True)
    def urunler_html(self, kategori_id=None):
        if not kategori_id:
            return request.render('kreatif.etkin_promosyon_urunler_page', {'data': {"error": "Kategori ID eksik!"}})

        url = "http://www.birikimpromosyon.com/api/json/"
        payload = {
            "ebayi_eposta": "info@kreatifcozumler.com",
            "hash": "892cfb16ebbdbdd8abb3630810a0792f",
            "tip": "array_kategori_urunler",
            "array_kategoriler": [int(kategori_id)]
        }
        headers = {
            "Content-Type": "application/json",
            "User-Agent": "kreatifcozumler.com",
        }

        try:
            response = requests.post(url, headers=headers, data=json.dumps(payload), timeout=20)
            response.raise_for_status()
            data = response.json()
            
            # Eğer gelen veri bir hata içeriyorsa
            if "Hata" in data:
                return request.render('kreatif.etkin_promosyon_urunler_page', {'data': {"error": data["Hata"]}})

            # Eğer API bir liste döndürüyorsa, sözlüğe dönüştür
            if isinstance(data, list):
                data = {"data": data}

        except requests.exceptions.RequestException as e:
            return request.render('kreatif.etkin_promosyon_urunler_page', {'data': {"error": str(e)}})
            # data = {"error": str(e)}

        return request.render('kreatif.etkin_promosyon_urunler_page', {'data': data})
    # https://www.kreatifcozumler.com/en/turuncu/varyant/urunler?kategori_id=13
    @http.route('/turuncu/varyant/urunler', type='http', auth='public', website=True)
    def varyant_urunler_html(self, kategori_id=None):
        """
        Seçilen kategoriye göre ürünleri listeleyen sayfa.
        """
        if not kategori_id:
            return request.render('kreatif.etkin_promosyon_varyant_urunler_page', {'data': {"error": "Kategori ID eksik!"}})

        url = "http://www.birikimpromosyon.com/api/json/"
        payload = {
            "ebayi_eposta": "info@kreatifcozumler.com",
            "hash": "892cfb16ebbdbdd8abb3630810a0792f",
            "tip": "array_varyant_kategori_urunler",
            "array_kategoriler": [int(kategori_id)]
        }
        headers = {
            "Content-Type": "application/json",
            "User-Agent": "kreatifcozumler.com",
        }

        try:
            response = requests.post(url, headers=headers, data=json.dumps(payload), timeout=20)
            response.raise_for_status()
            data = response.json()
            
            # Eğer gelen veri bir hata içeriyorsa
            if "Hata" in data:
                return request.render('kreatif.etkin_promosyon_varyant_urunler_page', {'data': {"error": data["Hata"]}})
        except requests.exceptions.RequestException as e:
            data = {"error": str(e)}

        return request.render('kreatif.etkin_promosyon_varyant_urunler_page', {'data': data})
    
    
    # https://kreatifcozumler.com/turuncu/varyant/urun-detay?kategori_id=13&urun_id=17699
    @http.route('/turuncu/varyant/urun-detay', type='http', auth='public', website=True)
    def varyant_urun_detay(self, kategori_id=None, urun_id=None):
        """
        Ürün Detayı Sayfası Controller
        """
        if not kategori_id or not urun_id:
            return request.render(
                'kreatif.etkin_promosyon_varyant_urunler_page',
                {'data': {"error": "Kategori veya Ürün ID eksik!"}}
            )

        # API'den veriyi çek
        url = "http://www.birikimpromosyon.com/api/json/"
        payload = {
            "ebayi_eposta": "info@kreatifcozumler.com",
            "hash": "892cfb16ebbdbdd8abb3630810a0792f",
            "tip": "array_varyant_kategori_urunler",
            "array_kategoriler": [int(kategori_id)]
        }
        headers = {
            "Content-Type": "application/json",
            "User-Agent": "kreatifcozumler.com",
        }

        try:
            response = requests.post(url, headers=headers, data=json.dumps(payload), timeout=20)
            response.raise_for_status()
            urunler = response.json()

            # Belirtilen ürün ID'ye göre filtreleme
            selected_urun = next((urun for urun in urunler if str(urun.get("urun_id")) == urun_id), None)

            if not selected_urun:
                return request.render(
                    'kreatif.etkin_promosyon_varyant_urunler_page',
                    {'data': {"error": f"Ürün ID {urun_id} bulunamadı!"}}
                )

            return request.render(
                'kreatif.etkin_promosyon_varyant_urun_detay_page',
                {'urun': selected_urun}
            )
        except requests.exceptions.RequestException as e:
            return request.render(
                'kreatif.etkin_promosyon_varyant_urunler_page',
                {'data': {"error": str(e)}}
            )


class APIJsonController(http.Controller):
    @http.route('/api/json', type='http', auth='public')
    def api_json(self):
        """
        JSON formatında API verisini döndürür.
        """
        # API çağrısı
        url = "http://www.birikimpromosyon.com/api/json/"
        payload = {
            "ebayi_eposta": "info@kreatifcozumler.com",
            "hash": "892cfb16ebbdbdd8abb3630810a0792f",
            "tip": "tum_kategoriler"
        }
        headers = {
            "Content-Type": "application/json",
            "User-Agent": "kreatifcozumler.com",
        }

        try:
            response = requests.post(url, headers=headers, data=json.dumps(payload), timeout=20)
            response.raise_for_status()
            data = response.json()
        except requests.exceptions.RequestException as e:
            data = {"error": str(e)}

        # JSON veriyi döndür
        return request.make_response(
            headers={'Content-Type': 'application/json'},
            data=json.dumps(data)
        )
    @http.route('/api/tekil_kategori', type='http', auth='public', methods=['GET'], website=True)
    def tekil_kategori(self, kategori_id=None):
        """
        Tekil kategori verisini GET ile alır.
        """
        if not kategori_id:
            return request.make_response(
                headers={'Content-Type': 'application/json'},
                data=json.dumps({"error": "Kategori ID parametresi eksik!"})
            )

        # API URL
        url = "http://www.birikimpromosyon.com/api/json/"

        # API Gönderilecek Parametreler
        payload = {
            "ebayi_eposta": "info@kreatifcozumler.com",
            "hash": "892cfb16ebbdbdd8abb3630810a0792f",
            "tip": "tekil_kategori",
            "kategori_id": int(kategori_id)  # kategori_id int olmalı
        }

        # HTTP Headers
        headers = {
            "Content-Type": "application/json",
            "User-Agent": "kreatifcozumler.com",
        }

        try:
            # API Çağrısı
            response = requests.post(url, headers=headers, data=json.dumps(payload), timeout=20)
            response.raise_for_status()
            data = response.json()
        except requests.exceptions.RequestException as e:
            data = {"error": str(e)}

        # Yanıtı JSON olarak döndür
        return request.make_response(
            headers={'Content-Type': 'application/json'},
            data=json.dumps(data)
        ) 

    @http.route('/api/dynamic', type='http', auth='public', methods=['GET'], website=True)
    def dynamic_api(self, tip=None, id=None):
        """
        Gelen `tip` parametresine göre API çağrısı yapar ve sonuç döner.
        """
        if not tip:
            return request.make_response(
                headers={'Content-Type': 'application/json'},
                data=json.dumps({"error": "Tip parametresi eksik!"})
            )

        # API URL
        url = "http://www.birikimpromosyon.com/api/json/"
        
        # API Payload
        payload = {
            "ebayi_eposta": "info@kreatifcozumler.com",
            "hash": "892cfb16ebbdbdd8abb3630810a0792f",
            "tip": tip
        }

        # Eğer bir ID parametresi varsa bunu da payload'a ekle
        if id:
            payload["id"] = id

        # Headers
        headers = {
            "Content-Type": "application/json",
            "User-Agent": "kreatifcozumler.com",
        }

        try:
            # API çağrısı
            response = requests.post(url, headers=headers, data=json.dumps(payload), timeout=20)
            response.raise_for_status()
            data = response.json()
        except requests.exceptions.RequestException as e:
            data = {"error": str(e)}

        # JSON olarak döndür
        return request.make_response(
            headers={'Content-Type': 'application/json'},
            data=json.dumps(data)
        )


    @http.route('/api/dynamic2', type='http', auth='public', methods=['GET'], website=True)
    def dynamic_api2(self, tip=None, id=None):
        """
        Gelen `tip` parametresine göre API çağrısı yapar ve sonuç döner.
        """
        if not tip:
            return request.make_response(
                headers={'Content-Type': 'application/json'},
                data=json.dumps({"error": "Tip parametresi eksik!"})
            )

        # API URL
        url = "http://www.birikimpromosyon.com/api/json/"
        
        # API Payload
        payload = {
            "ebayi_eposta": "info@kreatifcozumler.com",
            "hash": "892cfb16ebbdbdd8abb3630810a0792f",
            "tip": tip
        }

        # Eğer bir ID parametresi varsa bunu payload'a ekle
        if id:
            try:
                payload["id"] = int(id)  # ID'nin integer olduğundan emin olun
            except ValueError:
                return request.make_response(
                    headers={'Content-Type': 'application/json'},
                    data=json.dumps({"error": "ID parametresi geçerli bir sayı olmalıdır!"})
                )

        # Headers
        headers = {
            "Content-Type": "application/json",
            "User-Agent": "kreatifcozumler.com",
        }

        try:
            # API Çağrısı
            response = requests.post(url, headers=headers, data=json.dumps(payload), timeout=20)
            response.raise_for_status()  # HTTP Hataları için kontrol
            data = response.json()
        except requests.exceptions.RequestException as e:
            data = {"error": str(e)}

        # JSON olarak döndür
        return request.make_response(
            headers={'Content-Type': 'application/json'},
            data=json.dumps(data)
        )

    @http.route('/api/array_index', type='http', auth='public', methods=['GET'], website=True)
    def array_index(self, kategoriler=None, urunler=None):
        """
        Array Index API Çağrısı: GET isteği ile çalışır, belirtilen kategori ve ürün ID'leri ile API'ye istek gönderir.
        """
        # API URL
        url = "http://www.birikimpromosyon.com/api/json/"

        # E-Bayi bilgileri
        ebayi_eposta = "info@kreatifcozumler.com"
        hash_kodu = "892cfb16ebbdbdd8abb3630810a0792f"

        # Kategoriler ve Ürünler parametrelerini işle
        kategoriler_idler = [int(x) for x in kategoriler.split(',')] if kategoriler else []
        urunler_idler = [int(x) for x in urunler.split(',')] if urunler else []

        # Payload
        payload = {
            "ebayi_eposta": ebayi_eposta,
            "hash": hash_kodu,
            "tip": "array_index",
            "array_kategoriler": kategoriler_idler,
            "array_urunler": urunler_idler,
        }

        # HTTP Headers
        headers = {
            "Content-Type": "application/json",
            "User-Agent": "kreatifcozumler.com",  # www olmadan
        }

        try:
            # API Çağrısı
            response = requests.post(url, headers=headers, data=json.dumps(payload), timeout=20)
            response.raise_for_status()  # HTTP hataları için kontrol
            data = response.json()  # JSON Yanıt
        except requests.exceptions.RequestException as e:
            data = {"error": str(e)}

        # Yanıtı JSON olarak döndür
        return request.make_response(
            json.dumps(data),
            headers={'Content-Type': 'application/json'}
        )        


   
 
class APIHtmlController(http.Controller):
    
    @http.route('/api/turuncu/products', type='http', auth='public', website=True)
    def list_products(self):

        url = "https://www.kreatifcozumler.com/en/api/dynamic?tip=tum_urunler"
        try:
            # API'den veri çekme
            response = requests.get(url)
            response.raise_for_status()  # Hata varsa tetikler
            products = response.json()
        except requests.exceptions.RequestException as e:
            # Hata durumunda boş liste döndür
            products = []
            http.request.env.cr.rollback()  # DB bağlantısını temizle
            request.env['ir.logging'].sudo().create({
                'name': 'API Error',
                'type': 'server',
                'message': f"Error fetching products: {str(e)}",
                'level': 'error',
            })

        # Template'e veri gönder
        return request.render('kreatif.turuncu_product_list_template', {
            'products': products
        })



    @http.route('/api/turuncu/tum_urunler_varyant', auth='public', website=True)
    def get_products(self, **kwargs):
        # API URL'si
        api_url = "https://www.kreatifcozumler.com/en/api/dynamic?tip=tum_urunler_varyant"
        try:
            # API'den veri çekme
            response = requests.get(api_url)
            response.raise_for_status()  # Hata varsa tetikler
            products = response.json()  # JSON verisini çöz
        except requests.exceptions.RequestException as e:
            products = []  # Hata durumunda boş liste döndür
            request.env.cr.rollback()
            request.env['ir.logging'].sudo().create({
                'name': 'API Error',
                'type': 'server',
                'message': f"API Error: {str(e)}",
                'level': 'error',
            })

        # Şablonu render ederek ürünleri gönder
        return request.render('kreatif.tum_urunler_varyant_product_template', {
            'products': products
        })

    @http.route('/api/turuncu/tum_kategoriler', auth='public', website=True)
    def get_categories(self, **kwargs):
        # API URL'si
        api_url = "https://www.kreatifcozumler.com/en/api/dynamic?tip=tum_kategoriler"
        try:
            # API'den veri çekme
            response = requests.get(api_url)
            response.raise_for_status()
            categories = response.json()  # JSON verisini çöz
        except requests.exceptions.RequestException as e:
            categories = []  # Hata durumunda boş liste döndür
            request.env.cr.rollback()
            request.env['ir.logging'].sudo().create({
                'name': 'API Error',
                'type': 'server',
                'message': f"API Error: {str(e)}",
                'level': 'error',
            })

        # Şablonu render ederek kategorileri gönder
        return request.render('kreatif.tum_kategoriler_category_template', {
            'categories': categories
        })    

    @http.route('/api/turuncu/ustkategoriler', auth='public', website=True)
    def get_ustkategoriler(self, **kwargs):
        # API URL'si
        api_url = "https://www.kreatifcozumler.com/en/api/dynamic?tip=tum_ustkategoriler"
        try:
            # API'den veri çekme
            response = requests.get(api_url)
            response.raise_for_status()
            ustkategoriler = response.json()  # JSON verisini çöz
        except requests.exceptions.RequestException as e:
            ustkategoriler = []  # Hata durumunda boş liste döndür
            request.env.cr.rollback()
            request.env['ir.logging'].sudo().create({
                'name': 'API Error',
                'type': 'server',
                'message': f"API Error: {str(e)}",
                'level': 'error',
            })

        # Şablonu render ederek üst kategorileri gönder
        return request.render('kreatif.ustkategoriler_template', {
            'ustkategoriler': ustkategoriler
        }) 

    @http.route('/api/turuncu/altkategoriler', auth='public', website=True)
    def get_altkategoriler(self, **kwargs):
        # API URL'si
        api_url = "https://www.kreatifcozumler.com/en/api/dynamic?tip=tum_altkategoriler"
        try:
            # API'den veri çekme
            response = requests.get(api_url)
            response.raise_for_status()
            altkategoriler = response.json()  # JSON verisini çöz
        except requests.exceptions.RequestException as e:
            altkategoriler = []  # Hata durumunda boş liste döndür
            request.env.cr.rollback()
            request.env['ir.logging'].sudo().create({
                'name': 'API Error',
                'type': 'server',
                'message': f"API Error: {str(e)}",
                'level': 'error',
            })

        # Şablonu render ederek alt kategorileri gönder
        return request.render('kreatif.altkategoriler_template', {
            'altkategoriler': altkategoriler
        })   
    @http.route('/api/turuncu/kategoriler_hiyerasi', auth='public', website=True)
    def get_kategori_hiyerasi(self, **kwargs):
        # API URL'si
        api_url = "https://www.kreatifcozumler.com/en/api/dynamic?tip=tum_kategoriler_hiyerasi"
        try:
            # API'den veri çekme
            response = requests.get(api_url)
            response.raise_for_status()
            kategoriler_hiyerasi = response.json()  # JSON verisini çöz
        except requests.exceptions.RequestException as e:
            kategoriler_hiyerasi = []  # Hata durumunda boş liste döndür
            request.env.cr.rollback()
            request.env['ir.logging'].sudo().create({
                'name': 'API Error',
                'type': 'server',
                'message': f"API Error: {str(e)}",
                'level': 'error',
            })

        # Şablonu render ederek kategorileri gönder
        return request.render('kreatif.kategoriler_hiyerasi_template', {
            'kategoriler': kategoriler_hiyerasi
        })        

    @http.route('/api/html', type='http', auth='public', website=True)
    def api_html(self):
        url = "http://www.birikimpromosyon.com/api/json/"
        payload = {
            "ebayi_eposta": "info@kreatifcozumler.com",
            "hash": "892cfb16ebbdbdd8abb3630810a0792f",
            "tip": "tum_kategoriler"
        }
        headers = {
            "Content-Type": "application/json",
            "User-Agent": "kreatifcozumler.com",
        }

        try:
            response = requests.post(url, headers=headers, data=json.dumps(payload), timeout=20)
            response.raise_for_status()
            data = response.json()
        except requests.exceptions.RequestException as e:
            data = {"error": str(e)}

        # Gelen veri liste ise, sözlüğe dönüştür
        if isinstance(data, list):
            data = {"data": data, "error": None}
        elif isinstance(data, dict) and "error" not in data:
            data["error"] = None

        # Şablona gönder
        return request.render('kreatif.api_template', {'data': data})
    
    
    """ @http.route('/api/html', type='http', auth='public', website=True)
    def api_html(self):
         
        # HTML formatında API verisini döndürür.
        
        # API çağrısı
        url = "http://www.birikimpromosyon.com/api/json/"
        payload = {
            "ebayi_eposta": "info@kreatifcozumler.com",
            "hash": "892cfb16ebbdbdd8abb3630810a0792f",
            "tip": "tum_kategoriler"
        }
        headers = {
            "Content-Type": "application/json",
            "User-Agent": "kreatifcozumler.com",
        }

        try:
            response = requests.post(url, headers=headers, data=json.dumps(payload), timeout=20)
            response.raise_for_status()
            data = response.json()
        except requests.exceptions.RequestException as e:
            data = {"error": str(e)}

        # HTML veriyi döndür
        return request.render('kreatif.api_template', {'data': data})    """    


class APIController(http.Controller):

    @http.route('/api/data', type='http', auth='public', website=True)
    def api_data(self):
        # API çağrısı
        url = "http://www.birikimpromosyon.com/api/json/"
        payload = {
            "ebayi_eposta": "info@kreatifcozumler.com",
            "hash": "892cfb16ebbdbdd8abb3630810a0792f",
            "tip": "tum_kategoriler"
        }
        headers = {
            "Content-Type": "application/json",
            "User-Agent": "kreatifcozumler.com",
        }

        try:
            response = requests.post(url, headers=headers, data=json.dumps(payload), timeout=20)
            response.raise_for_status()
            data = response.json()
        except requests.exceptions.RequestException as e:
            data = {"error": str(e)}

        # Gelen veriyi template'e gönder
        return request.render('kreatif.api_template', {'data': data})

class CustomSnippets(http.Controller):
    @http.route(['/transfer/cart_content'], type='http', auth="public", website=True)
    def cart(self):
        products = request.website.sale_get_order().order_line.product_id
        data = []
        for product in products:
            fields = product.read(['display_name', 'description_sale', 'list_price', 'website_url'])[0];
            fields['image'] = request.env['website'].image_url(product, 'image_512')
            data.append(fields)
        return request.env['ir.ui.view']._render_template('transfer.s_cart_products_card', {'products': data})

class storyProfileReq(http.Controller):

    @http.route(['/create/story-report'], type="json", auth="public", methods=["POST"], cors='*', csrf=False)
    def create_story_report(self):
        data = json.loads(request.httprequest.data)
        val = {
            'partner_id': data['params']['partner_id'],
            'lat': data['params']['lat'],
            'lng': data['params']['lng']
            }
        create = request.env['story.profile'].sudo().create(val)
        result = {"code": 200, "message": "Created Successfully"}
        return result

    @http.route(['/nfc/profile/<card_id>'], type="http", auth="public", methods=["GET"], cors='*', website=True, csrf=False)
    def nfc_profile_analyze(self,card_id):
        story = http.request.env['story.profile'].sudo().search([["card_id","ilike",card_id]],limit=1)
        qr = http.request.env['qidgenerator.qidgenerator'].sudo().search([["card_id","=",card_id]],limit=1)
        if qr:  
            if story:
                return request.render("website.nfc-profile", {'contact': story.card_owner, 'story': story})
            else:
                return request.render("website.nfc-signup-form", {'card_id': card_id})
        else:
            return request.render("website.contactus_thanks_ea2f2e_70ad58_ef8852")

    @http.route(['/panel/touch/<card_id>'], type="http", auth="public", methods=["GET"], cors='*', website=True, csrf=False)
    def old_cards_analyze(self,card_id):
        story = http.request.env['story.profile'].sudo().search([["card_id","=",card_id]],limit=1)
        qr = http.request.env['qidgenerator.qidgenerator'].sudo().search([["card_id","=",card_id]],limit=1)
        if qr:  
            if story:
                return request.render("website.nfc-profile", {'contact': story.card_owner, 'story': story})
            else:
                return request.render("website.nfc-signup-form", {'card_id': card_id})
        else:
            return request.render("website.contactus_thanks_ea2f2e_70ad58_ef8852")

    @http.route(['/profile/<card_id>'], type="http", auth="public", methods=["GET"], cors='*', website=True, csrf=False)
    def old_text_cards_analyze(self,card_id):
        story = http.request.env['story.profile'].sudo().search([["name","=",card_id]],limit=1)
        qr = http.request.env['qidgenerator.qidgenerator'].sudo().search([["card_id","=",card_id]],limit=1)
        if qr:  
            if story:
                return request.render("website.nfc-profile", {'contact': story.card_owner, 'story': story})
            else:
                return request.render("website.nfc-signup-form", {'card_id': card_id})
        else:
            return request.render("website.contactus_thanks_ea2f2e_70ad58_ef8852")

    
    @http.route(['/profile/<card_id>'], type="http", auth="public", methods=["GET"], cors='*', website=True, csrf=False)
    def old_nfc_profile_analyze(self,card_id):
        story = http.request.env['story.profile'].sudo().search([["card_id","=",card_id]],limit=1)
        qr = http.request.env['qidgenerator.qidgenerator'].sudo().search([["card_id","=",card_id]],limit=1)
        if qr:  
            if story:
                return request.render("website.nfc-profile", {'contact': story.card_owner, 'story': story})
            else:
                return request.render("website.nfc-signup-form", {'card_id': card_id})
        else:
            return request.render("website.contactus_thanks_ea2f2e_70ad58_ef8852")
        

    @http.route('/nfc/profile/form', type="http", auth="public", website=True,  csrf=False)
    def create_nfc_profile(self, **kw):
        print("Data Received.....", kw)
        # story_vals = {
        #      'card_id': kw.get('from_id'),
        #      'to': kw.get('to_id'),
        #      'currency': kw.get('currency_id')
        #  }
        result = http.request.env['res.users'].sudo().search(["|",["login","=",kw.get('login')],["x_card_id","=",kw.get('x_card_id')]],limit=1)
        if result:
            return request.render("website.contactus_thanks_ea2f2e_70ad58", {'obj': kw})
        else:
            contact = request.env['res.users'].sudo().create(kw)
            return request.render("website.contactus_thanks_ea2f2e", {'obj': kw})

    @http.route('/connect/form', type="http", auth="public", website=True,  csrf=False)
    def create_connect(self, **kw):
        # story_vals = {
        #      'card_id': kw.get('from_id'),
        #      'to': kw.get('to_id'),
        #      'currency': kw.get('currency_id')
        #  }
        result = http.request.env['story.profile'].sudo().search([["card_id","ilike",kw.get('card_id')]],limit=1)
        if result:
            last_connected_contacts = ""
            if "#Name:" not in str(result.connected_contacts):
                last_connected_contacts = ""
            else:
                last_connected_contacts = str(result.connected_contacts) + "\n\n"
            result["connected_contacts"] = False
            surname = kw.get('name').split()[len(kw.get('name').split())-1]
            result["last_connected_contact_surname"] = surname
            result["last_connected_contact_mobile"] = kw.get('mobile')
            result["last_connected_contact_email"] = kw.get('email')
            result["last_connected_contact_country"] = kw.get('country')
            result["connected_contacts"] = last_connected_contacts + "#Name: " + str(kw.get('name')) + "\nMobile: " + str(kw.get('mobile')) + "\nEmail: " + str(kw.get('email')) + "\nAddress: " + str(kw.get('address')) + "\nCountry: " + str(kw.get('country')) + "\nZip Code: " + str(kw.get('zip'))
            result["last_connected_contact_name"] = kw.get('name').replace(surname, "")
            # template_obj = http.request.env['mail.template'].sudo().search([['id','=',36]], limit=1)
            # template_id = template_obj
            # template = http.request.env['mail.template'].browse(template_id.id)

            # # Prepare the template values
            # template_values = {
            #     'object': result,
            #     'company_id': http.request.env['res.company'].sudo().search([['id','=',1]], limit=1),
            #     'email_from': "info@businesstouch.com.tr",
            #     'email_to': result.email
            # }


            # # Render the email template
            # email_body = http.request.env['mail.template']._render_template(self.body, self.model, [result.id], post_process=True)

            # # Send the email
            # mail = http.request.env['mail.mail'].sudo().create({
            #     'subject': 'Test - {}'.format(result.name),
            #     'body': email_body,
            #     'email_from': "info@businesstouch.com.tr"l,
            #     'email_to': result.email,
            # })
            # mail.send()

            # Render the template with the values
            # if template_obj:
                
            #     receipt_list = [result.email]
            #     email_cc = []
            #     email_body = template_id.render_body(template_values)
            #     #body = "test"
            #     #rendered_template = template._render_template(template.body_html, template.model, [result.id])
            #     mail_values = {
            #     'subject': template_id.subject,
            #     'body_html': email_body,
            #     'email_to':';'.join(map(lambda x: x, receipt_list)),
            #     'email_cc':';'.join(map(lambda x: x, email_cc)),
            #     'email_from': "info@businesstouch.com.tr"
            #     }
            #     create_email_message = http.request.env['mail.mail'].create(mail_values)

            #     content_string = "This is the content of the file."
            #     # Encode bytes in Base64
            #     base64_encoded = base64.b64encode(content_string.encode('utf-8'))
            #     # Attach the VCF file to the email
            #     attachment_name = f"{kw.get('name')}.vcf"
            #     attachment_data = base64_encoded
            #     attachment_id = http.request.env['ir.attachment'].create({
            #         'name': attachment_name,
            #         'datas': attachment_data,
            #         'res_model': 'mail.mail',
            #         'res_id': create_email_message.id,
            #         'type': 'binary'
            #     })
            #     attachments_list = []
            #     attachments_list.append(attachment_id.id)
            #     mail_values['attachment_ids'] = [(6, 0,attachments_list)]
            #     #template_id.with_context(mail_values).send_mail(result.id, email_values=mail_values)
            #     send_email = create_email_message.send()
            return request.render("website.contactus_thanks_5eb5a0", {'obj': kw})
        else:
            return request.render("website.contactus_thanks_5eb5a0_4aa62a", {'obj': kw})
        
    @http.route('/comment/form', type="http", auth="public", website=True,  csrf=False)
    def create_comment(self, **kw):
        # story_vals = {
        #      'card_id': kw.get('from_id'),
        #      'to': kw.get('to_id'),
        #      'currency': kw.get('currency_id')
        #  }
        result = http.request.env['story.profile'].sudo().search([["card_id","ilike",kw.get('card_id')]],limit=1)
        if result:
            now = datetime.now()
            last_comments = ""
            if "#" not in str(result.comments):
                last_comments = ""
            else:
                last_comments = str(result.comments) + "\n\n"
            result["comments"] = False
            result["comments"] = last_comments + "#" + str(now.strftime("%d-%m-%Y %H:%M:%S")) + "-" + str(kw.get('name')) + " - " + str(kw.get('comment'))
            return request.render("website.contactus_thanks_5eb5a0_39c708", {'obj': kw})
        else:
            return request.render("website.contactus_thanks_5eb5a0_4aa62a", {'obj': kw})

    
    @http.route(['/create/report-for-device'], type="json", auth="public", methods=["POST"], cors='*', csrf=False)
    def create_device_req_1(self):
        data = json.loads(request.httprequest.data)
        device_id = http.request.env['story.profile'].sudo().search([["device_id","=",data['params']['device_id']]],limit=1)
        if len(device_id) > 0:
            result = ""
            if data['params']['device_update'] == 2:
                device_id.device_update = False
            if data['params']['device_update'] == 0:
                device_id.device_update = True
            if data['params']['create_report'] == False and device_id.device_update == False:
                result = {"code": 200, "message": "Idle Ask Successfully"}
            if data['params']['create_report'] == False and device_id.device_update == True:
                settings = http.request.env['settings.profile'].sudo().search([["device_id.device_id","=",data['params']['device_id']]],limit=1)
                result = {"code": 200, "message": "Idle Ask Successfully", "device_update": device_id.device_update, "device_status": device_id.device_status, "device_status_1": device_id.device_status_1, "device_status_2": device_id.device_status_2, "device_status_3": device_id.device_status_3, "device_status_4": device_id.device_status_4, "device_status_5": device_id.device_status_5, "device_status_6": device_id.device_status_6, "device_status_7": device_id.device_status_7, "device_status_8": device_id.device_status_8, "device_status_9": device_id.device_status_9, "device_status_10": device_id.device_status_10, "device_status_11": device_id.device_status_11, "device_status_12": device_id.device_status_12, "device_status_13": device_id.device_status_13, "device_status_14": device_id.device_status_14, "device_status_15": device_id.device_status_15, "device_status_16": device_id.device_status_16, "setting_1_value": settings.setting_1_value, "setting_2_value": settings.setting_2_value, "setting_3_value": settings.setting_3_value, "setting_4_value": settings.setting_4_value, "setting_5_value": settings.setting_5_value, "setting_6_value": settings.setting_6_value, "setting_7_value": settings.setting_7_value, "setting_8_value": settings.setting_8_value, "setting_9_value": settings.setting_9_value, "setting_10_value": settings.setting_10_value, "entrance_delay_time": settings.entrance_delay_time, "exit_delay_time": settings.exit_delay_time, "alarm_time": settings.alarm_time, "default_settings_1": settings.default_settings_1, "zone_status_1": settings.zone_status_1, "always_on_1": settings.always_on_1, "sudden_alarm_1": settings.sudden_alarm_1, "default_settings_2": settings.default_settings_2, "zone_status_2": settings.zone_status_2, "always_on_2": settings.always_on_2, "sudden_alarm_2": settings.sudden_alarm_2, "default_settings_3": settings.default_settings_3, "zone_status_3": settings.zone_status_3, "always_on_3": settings.always_on_3, "sudden_alarm_3": settings.sudden_alarm_3, "default_settings_4": settings.default_settings_4, "zone_status_4": settings.zone_status_4, "always_on_4": settings.always_on_4, "sudden_alarm_4": settings.sudden_alarm_4, "wifi_name": settings.wifi_name, "wifi_password": settings.wifi_password, "test_signal_time": settings.test_signal_time, "last_value": 1}
            if data['params']['create_report'] == True and device_id.device_update == False:
                val = {
                'device_id': device_id.id,
                'ademco_id': data['params']['code'],
                'zone': data['params']['zone'],
                #'date': datetime.now()
                }
                create = request.env['reports.profile'].sudo().create(val)
                result = {"code": 200, "message": "Live Report Created Successfully"}
            if data['params']['create_report'] == True and device_id.device_update == True:
                settings = http.request.env['settings.profile'].sudo().search([["device_id.device_id","=",data['params']['device_id']]],limit=1)
                val = {
                'device_id': device_id.id,
                'ademco_id': data['params']['code'],
                'zone': data['params']['zone'],
                #'date': datetime.now()
                }
                create = request.env['reports.profile'].sudo().create(val)
                result = {"code": 200, "message": "Live Report Created Successfully", "device_update": device_id.device_update, "device_status": device_id.device_status, "device_status_1": device_id.device_status_1, "device_status_2": device_id.device_status_2, "device_status_3": device_id.device_status_3, "device_status_4": device_id.device_status_4, "device_status_5": device_id.device_status_5, "device_status_6": device_id.device_status_6, "device_status_7": device_id.device_status_7, "device_status_8": device_id.device_status_8, "device_status_9": device_id.device_status_9, "device_status_10": device_id.device_status_10, "device_status_11": device_id.device_status_11, "device_status_12": device_id.device_status_12, "device_status_13": device_id.device_status_13, "device_status_14": device_id.device_status_14, "device_status_15": device_id.device_status_15, "device_status_16": device_id.device_status_16, "setting_1_value": settings.setting_1_value, "setting_2_value": settings.setting_2_value, "setting_3_value": settings.setting_3_value, "setting_4_value": settings.setting_4_value, "setting_5_value": settings.setting_5_value, "setting_6_value": settings.setting_6_value, "setting_7_value": settings.setting_7_value, "setting_8_value": settings.setting_8_value, "setting_9_value": settings.setting_9_value, "setting_10_value": settings.setting_10_value, "entrance_delay_time": settings.entrance_delay_time, "exit_delay_time": settings.exit_delay_time, "alarm_time": settings.alarm_time, "default_settings_1": settings.default_settings_1, "zone_status_1": settings.zone_status_1, "always_on_1": settings.always_on_1, "sudden_alarm_1": settings.sudden_alarm_1, "default_settings_2": settings.default_settings_2, "zone_status_2": settings.zone_status_2, "always_on_2": settings.always_on_2, "sudden_alarm_2": settings.sudden_alarm_2, "default_settings_3": settings.default_settings_3, "zone_status_3": settings.zone_status_3, "always_on_3": settings.always_on_3, "sudden_alarm_3": settings.sudden_alarm_3, "default_settings_4": settings.default_settings_4, "zone_status_4": settings.zone_status_4, "always_on_4": settings.always_on_4, "sudden_alarm_4": settings.sudden_alarm_4, "wifi_name": settings.wifi_name, "wifi_password": settings.wifi_password, "test_signal_time": settings.test_signal_time, "last_value": 1}
            return result
        else:
            return "no"

    @http.route(['/create/report-for-device-gsm'], type="http", auth="public", methods=["GET"], cors='*', csrf=False)
    def create_device_req_gsm_2(self):
        return "{'code': 200, 'message': 'Idle Ask Successfully'}"


    @http.route('/chplayerid/<email>/<player_id>', type='http', auth="public", methods=["GET"], cors='*', website=False)
    def write_Playerid(self, email,player_id):
        # get the information using the SUPER USER
        result = "not found"
        contact = http.request.env['res.partner'].sudo().search([['email','=', str(email)]])
        if len(contact) == 1:
            contact['player_id'] = player_id
            result = "ok"
        return result


    # @http.route(['/create/report-for-device'], type="json", auth="public", methods=["POST"], csrf=False)
    # def create_device_req_1(self, **kw):
    #     print("Data Received.....", kw)  
    #     return "hello"
    
    # @http.route('/my_module/xxx', type='json', auth='none', methods=['POST']) 
    # def my_foo(self, **post):
    #     data = request.jsonrequest
    #     return data



class transferProfileReq(http.Controller):
    
    #widget transfer booking
    @http.route('/create/form-1', type="http", auth="public", website=True,  csrf=False)
    def create_form_req_1(self, **kw):
        print("Data Received.....", kw)
        request.env['transfer.profile'].sudo().create(kw)
        vals = {
             'from': kw.get('from_id'),
             'to': kw.get('to_id'),
             'currency': kw.get('currency_id')
         }
         
        result = http.request.env['product.template'].sudo().search(["|","&",["from_id.id","=",kw.get('from_id')],["to_id.id","=",kw.get('to_id')],"&",["from_id.id","=",kw.get('to_id')],["to_id.id","=",kw.get('from_id')]],limit=1)
        if result:
            return request.render("transfer.form_response_1", {'form_1_details': kw, 'product':result})
        else:
            return request.render("transfer.form_response_4", {'form_1_details': kw, 'product':result})
        
    #car select
    @http.route('/create/form-2', type="http", auth="public", website=True,  csrf=False)
    def create_form_req_2(self, **kw):
        vals = {
             'product': kw.get('product_id'),
             'car': kw.get('car_id'),
             'price': kw.get('price'),
             'currency': kw.get('currency_id')
         }
        return request.render("transfer.form_response_2", {'form_2_details': vals})

    #reservation details
    @http.route('/create/form-3', type="http", auth="public", website=True,  csrf=False)
    def create_form_req_3(self, **kw):
        vals = {
             'id_of_product': kw.get('id_of_product'),
             'from_id': kw.get('from_id'),
             'to_id': kw.get('to_id'),
             'currency': kw.get('currency'),
             'going_transfer_date': kw.get('going_transfer_date'),
             'going_transfer_time': kw.get('going_transfer_time'),
             'going_flight_no': kw.get('going_flight_no'),
             'going_destination': kw.get('going_destination'),
             'return_status': kw.get('return_status'),
             'coming_transfer_date': kw.get('coming_transfer_date'),
             'coming_transfer_time': kw.get('coming_transfer_time'),
             'coming_flight_no': kw.get('coming_flight_no'),
             'coming_destination': kw.get('coming_destination'),
             'special_note': kw.get('special_note'),
             'passenger_number': kw.get('passenger_number'),
             'child_number': kw.get('child_number'),
             'baby_number': kw.get('baby_number'),
             'welcome_status': kw.get('welcome_status'),
             'baby_seat_number': kw.get('baby_seat_number'),
             'booster_seat_number': kw.get('booster_seat_number'),
             'stroller_seat_number': kw.get('stroller_seat_number'),
             'promotion_code': kw.get('promotion_code'),
             'customer_name': kw.get('customer_name'),
             'customer_surname': kw.get('customer_surname'),
             'customer_email': kw.get('customer_email'),
             'customer_phone': kw.get('customer_phone'),
             'another_passengers': kw.get('another_passengers'),
             'price': kw.get('price'),
             'car_name': kw.get('car_name'),
             'car_type': kw.get('car_type'),
             'car_id': kw.get('car_id')
         }
        
        partner_id = http.request.env['res.partner'].sudo().search(["&","&",["name","=",vals['customer_name']],["phone","=",vals['customer_phone']],["email","=",vals['customer_email']]])
        if len(partner_id) == 0:
            request.env['res.partner'].sudo().create({
            'name': vals['customer_name'] + " " + vals['customer_surname'],
            'email': vals['customer_email'],
            'phone': vals['customer_phone']
            })
        
        partner_id = http.request.env['res.partner'].sudo().search(["&","&",["name","=",vals['customer_name'] + " " + vals['customer_surname']],["phone","=",vals['customer_phone']],["email","=",vals['customer_email']]])
        from_id = http.request.env['transfer.city'].sudo().search([["name", "=", vals['from_id']]])
        to_id = http.request.env['transfer.city'].sudo().search([["name", "=", vals['to_id']]])
        currency_id = http.request.env['res.currency'].sudo().search([["name", "=", vals['currency']]])
        product = http.request.env['product.template'].sudo().search([["id", "=", vals['id_of_product']]])
        pricelist_id = http.request.env['product.pricelist'].sudo().search([["currency_id.id", "=", currency_id.id]])
        
        sale_order = request.env['sale.order'].sudo().create({
        'partner_id': partner_id.id,
        'pricelist_id': pricelist_id.id,
        'date_order': datetime.now(),
        
        'id_of_product': vals['id_of_product'],
        'from_id': from_id.id,
        'to_id': to_id.id,
        'currency': vals['currency'],
        'going_transfer_date': vals['going_transfer_date'],
        'going_transfer_time': vals['going_transfer_time'],
        'going_flight_no': vals['going_flight_no'],
        'going_destination': vals['going_destination'],
        'return_status': vals['return_status'],
        'coming_transfer_date': vals['coming_transfer_date'],
        'coming_transfer_time': vals['coming_transfer_time'],
        'coming_flight_no': vals['coming_flight_no'],
        'coming_destination': vals['coming_destination'],
        'special_note': vals['special_note'],
        'passenger_number': vals['passenger_number'],
        'child_number': vals['child_number'],
        'baby_number': vals['baby_number'],
        'welcome_status': vals['welcome_status'],
        'baby_seat_number': vals['baby_seat_number'],
        'booster_seat_number': vals['booster_seat_number'],
        'stroller_seat_number': vals['stroller_seat_number'],
        'promotion_code': vals['promotion_code'],
        'customer_name': vals['customer_name'],
        'customer_surname': vals['customer_surname'],
        'customer_email': vals['customer_email'],
        'customer_phone': vals['customer_phone'],
        'another_passengers': vals['another_passengers'],
        'price': vals['price'],
        'car_name': vals['car_name'],
        'car_type': vals['car_type'],
        'car_id': vals['car_id'],
        #"order_line":[(0,0,{"sequence":10,"display_type":False,"product_uom_qty":1,"qty_delivered":0,"qty_delivered_manual":0,"customer_lead":0,"price_unit":vals['price'],"discount":0,"product_id":sale_order_line.product_id.id,"product_template_id":product.id,"name":product.name,"product_uom":1})]
        
        })
        prd = http.request.env['product.product'].sudo().search([["name", "=", product.name]])
        sale_order.write({
            'order_line': [(0,0, {'product_id':prd.id,"name":product.name,"price_unit":vals['price'],"product_uom_qty":1})]
        })
        #product_id = http.request.env['product.product'].search([],limit=1)
        #sale_order_line = request.env['sale.order.line'].create({  
        #                      'product_id': product.id, 
        #                      "name":product.name,
        #                      "price_unit":vals['price'],
        #                      "product_uom_qty":1,
        #                      "order_id":
        #                    })

        return request.render("transfer.form_response_3", {'form_3_details': vals})