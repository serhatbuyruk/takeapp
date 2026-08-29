import base64
import json
import logging
import mimetypes
import os
import re
from odoo import fields, http
from odoo.http import request, Stream

_logger = logging.getLogger(__name__)
_ONESIGNAL_SUBSCRIPTION_ID_PATTERN = re.compile(
    r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$',
    re.IGNORECASE,
)


class CourierAccountingPortal(http.Controller):

    @http.route('/kurye-muhasebe/main-website-domain', type='http', auth='public', methods=['GET'], website=False, csrf=False, sitemap=False)
    def main_website_domain(self, **kw):
        domain = request.env['ir.config_parameter'].sudo().get_param(
            'partner_courier_accounting.main_website_domain',
            '',
        )
        return request.make_response(
            json.dumps({'main_website_domain': (domain or '').strip()}),
            [('Content-Type', 'application/json; charset=utf-8')],
        )

    @http.route('/kurye-muhasebe/player-id', type='json', auth='public', methods=['POST'], csrf=False)
    def save_player_id(self, playerId=None, player_id=None, contactId=None, contact_id=None, **kw):
        partner = self._partner()
        if not partner:
            return {'success': False, 'error': 'not_logged_in'}

        requested_contact_id = contactId or contact_id
        if requested_contact_id:
            try:
                requested_contact_id = int(requested_contact_id)
            except (TypeError, ValueError):
                return {'success': False, 'error': 'invalid_contact_id'}
            if requested_contact_id != partner.id:
                return {'success': False, 'error': 'contact_mismatch'}

        player_id_value = (playerId or player_id or '').strip()
        if not player_id_value:
            return {'success': False, 'error': 'missing_player_id'}
        if not _ONESIGNAL_SUBSCRIPTION_ID_PATTERN.match(player_id_value):
            _logger.warning(
                'Invalid OneSignal player_id rejected for partner %s: %s',
                partner.id,
                player_id_value,
            )
            return {'success': False, 'error': 'invalid_player_id'}

        partner.sudo().write({'player_id': player_id_value})
        return {
            'success': True,
            'contactId': partner.id,
            'playerId': player_id_value,
        }

    def _partner(self):
        partner_id = request.session.get('courier_accounting_partner_id')
        if not partner_id:
            return request.env['res.partner']
        partner = request.env['res.partner'].sudo().browse(partner_id).exists()
        if not partner or not partner.active:
            request.session.pop('courier_accounting_partner_id', None)
            return request.env['res.partner']
        return partner

    def _render(self, template, values=None):
        values = values or {}
        values['partner'] = values.get('partner') or self._partner()
        return request.render(template, values)

    def _format_money(self, amount, currency):
        amount = amount or 0.0
        text = f'{amount:,.2f}'.replace(',', 'X').replace('.', ',').replace('X', '.')
        return f'{currency.symbol or ""}{text}'

    def _format_percent(self, amount):
        text = f'{amount or 0:.0f}'.replace('.', ',')
        return f'%{text}'

    def _parse_amount(self, value):
        text = (value or '').strip()
        if not text:
            return 0.0
        normalized = text.replace(' ', '')
        if ',' in normalized and '.' in normalized:
            normalized = normalized.replace('.', '').replace(',', '.')
        else:
            normalized = normalized.replace(',', '.')
        try:
            return float(normalized)
        except ValueError:
            return 0.0

    def _format_date(self, value):
        return value.strftime('%d/%m/%Y') if value else ''

    def _phone_url(self, phone):
        digits = ''.join(char for char in (phone or '') if char.isdigit())
        if not digits:
            return ''
        if digits.startswith('90') and len(digits) == 12:
            return 'tel:+%s' % digits
        if digits.startswith('0') and len(digits) == 11:
            return 'tel:+90%s' % digits[1:]
        if digits.startswith('5') and len(digits) == 10:
            return 'tel:+90%s' % digits
        return 'tel:+%s' % digits

    def _contact_centers(self):
        return [
            {
                'name': 'Seyhan İletişim Merkezi - Adana',
                'address': [
                    'Mithatpaşa Mah. Alparslan Türkeş Bulvarı',
                    'No:51B 23 ve 24 Bağımsız Bölümler',
                    'Seyhan Adana',
                ],
                'phone': '(0850) 969 73 80',
                'days': 'Pazartesi - Cumartesi',
                'hours': '10:00 - 18:00',
                'other_cities': 'Batman, Diyarbakır, Gaziantep, Hatay, Kahramanmaraş, Mardin ve Mersin',
            },
            {
                'name': 'Çankaya İletişim Merkezi - Ankara',
                'address': [
                    'Aşıkpaşa Mah. Vedat Dalokay Cd. No:85/B 06670',
                    'Çankaya/Ankara',
                ],
                'phone': '(0850) 969 73 80',
                'days': 'Pazartesi - Cumartesi',
                'hours': '10:00 - 18:00',
                'other_cities': 'Elazığ, Erzurum, Kayseri, Malatya, Aksaray, Çorum, Sivas, Tokat, Van',
            },
            {
                'name': 'Lara İletişim Merkezi - Antalya',
                'address': [
                    'Zümrütova Mah. Sinanoğlu cad. No:29/A',
                    'Muratpaşa Antalya',
                ],
                'phone': '(0850) 969 73 80',
                'days': 'Pazartesi - Cumartesi',
                'hours': '10:00 - 18:00',
                'other_cities': 'Denizli, Isparta, Konya, Fethiye',
            },
            {
                'name': 'Beşiktaş İletişim Merkezi',
                'address': [
                    'Muradiye Mah. Nüzhetiye Cd.',
                    'No:27/A İstanbul Beşiktaş',
                ],
                'phone': '(0850) 969 73 80',
                'days': 'Pazartesi - Cumartesi',
                'hours': '10:00 - 18:00',
                'other_cities': '',
            },
            {
                'name': 'Görükle İletişim Merkezi - Bursa',
                'address': [
                    'Dumlupınar Mah. Atatürk (500) Bul. A Blok Apt',
                    'No:53 A/A Görükle Bursa',
                ],
                'phone': '(0850) 969 73 80',
                'days': 'Pazartesi - Cumartesi',
                'hours': '10:00 - 18:00',
                'other_cities': 'Balıkesir, Bolu, Bursa, Çanakkale, Düzce, Eskişehir, Karabük, Kütahya, Sakarya, Yalova, Zonguldak, Afyon ve Uşak',
            },
            {
                'name': 'Çekmeköy İletişim Merkezi',
                'address': [
                    'Madenler Mah. Kıraçlar Sok. No:8',
                    'A Zemin Kat Merkez',
                ],
                'phone': '(0850) 969 73 80',
                'days': 'Pazartesi - Cuma',
                'hours': '10:00 - 18:00',
                'other_cities': 'Kocaeli',
            },
            {
                'name': 'Hasanpaşa İletişim Merkezi',
                'address': [
                    'Hasanpaşa, Uzunçayır Cd.',
                    '34722 No:55 C',
                ],
                'phone': '(0850) 969 73 80',
                'days': 'Pazartesi - Cumartesi',
                'hours': '10:00 - 18:00',
                'other_cities': 'Samsun, Trabzon, Rize, Giresun ve Ordu',
            },
            {
                'name': 'Çiğli İletişim Merkezi - İzmir',
                'address': [
                    'Anadolu cad. No:1036 A',
                    'Küçükçiğli Mahallesi Çiğli İzmir',
                ],
                'phone': '(0850) 969 73 80',
                'days': 'Pazartesi - Cumartesi',
                'hours': '10:00 - 18:00',
                'other_cities': 'Aydın, Manisa, Muğla (Fethiye hariç)',
            },
            {
                'name': 'Küçükçekmece İletişim Merkezi',
                'address': [
                    'İnönü Mahallesi, 1320. Çıkmaz Sk.',
                    'No:3/C Küçükçekmece/İstanbul',
                ],
                'phone': '(0850) 969 73 80',
                'days': 'Pazartesi - Cumartesi',
                'hours': '10:00 - 18:00',
                'other_cities': 'Edirne, Kırklareli, Tekirdağ',
            },
        ]

    def _training(self, training_id):
        return request.env['partner.courier.training'].sudo().search([
            ('id', '=', training_id),
            ('active', '=', True),
        ], limit=1)

    def _has_attended_training(self, training, partner):
        return bool(request.env['partner.courier.training.attendance'].sudo().search_count([
            ('training_id', '=', training.id),
            ('partner_id', '=', partner.id),
        ]))

    def _line_values(self, line):
        currency = line.currency_id or request.env.company.currency_id
        money_fields = [
            'pickup_amount', 'dropoff_amount', 'distance_amount', 'weekly_extra_package_amount',
            'tip_amount_tax_excluded', 'cash_deduction_tax_included', 'softpos_deduction_tax_included',
            'insurance_deduction_amount', 'field_deduction_order_amount',
            'advance_amount', 'isg_payment_amount', 'sgk_amount',
            'ixopay_cash_deposit_amount', 'total_deduction_amount',
            'kuryetec_bonus_tax_excluded', 'total_payment_tax_excluded',
            'bonus_included_total_payment_tax_excluded', 'bonus_included_earning_tax_included',
            'withholding_tax_amount', 'net_payable_amount',
        ]
        values = {field: self._format_money(line[field], currency) for field in money_fields}
        return values

    def _line_descriptions(self):
        return {
            'rider_id': 'Kurye için sistemde tanımlı benzersiz kullanıcı kimlik numarasıdır. Excel importunda bu numara kullanılarak hakediş satırı ilgili kurye kartına bağlanır.',
            'rider_name': 'Hakediş kaydının bağlı olduğu kurye ad soyad bilgisidir.',
            'area': 'Kuryenin ilgili haftada çalıştığı bölge veya ilçe bilgisidir.',
            'city': 'Kuryenin ilgili haftada çalıştığı şehir veya operasyon alanı bilgisidir.',
            'week': 'Hakedişin ait olduğu başlangıç ve bitiş tarih aralığıdır.',
            'payment_note': 'Ödeme, fatura veya hakedişle ilgili açıklama bilgisidir.',
            'pickup_count': 'İlgili haftada kuryenin tamamladığı tekli paket alma sayısıdır.',
            'dropoff_count': 'İlgili haftada kuryenin tamamladığı çoklu paket veya teslimat sayısıdır.',
            'pickup_amount': 'Tekli paketlerden hesaplanan haftalık kazanç tutarıdır.',
            'dropoff_amount': 'Çoklu paket veya teslimat işlemlerinden hesaplanan haftalık kazanç tutarıdır.',
            'distance_amount': 'Tekli ve çoklu paketlerde oluşan mesafeye göre hesaplanan kilometre bazlı toplam tutardır.',
            'weekly_extra_package_amount': 'Haftalık performans, paket adedi veya kampanya kriterlerine göre eklenen ek paket bonus tutarıdır.',
            'tip_amount_tax_excluded': 'Müşteri bahşişlerinin KDV hariç hesaplanan haftalık toplamıdır.',
            'cash_deduction_tax_included': 'Kuryenin elden aldığı nakit siparişlerden kaynaklanan KDV dahil kesinti tutarıdır.',
            'softpos_deduction_tax_included': 'SoftPos veya kredi kartı tahsilatlarından kaynaklanan KDV dahil kesinti tutarıdır.',
            'insurance_deduction_amount': 'İlgili hafta için uygulanan Yemeksepeti zorunlu sağlık sigortası kesintisi tutarıdır.',
            'field_deduction_order_amount': 'Saha operasyonu veya sipariş süreçlerinden kaynaklanan kesinti tutarıdır.',
            'advance_amount': 'İlgili hafta hakedişinden mahsup edilen avans tutarıdır.',
            'isg_payment_amount': 'İlgili hafta için İSG ödeme tutarıdır.',
            'sgk_amount': 'İlgili hafta için sigorta tutarıdır.',
            'ixopay_cash_deposit_amount': 'Kuryenin nakit olarak yatırdığı tutardır. Nakit kesinti hesabında mahsup edilir.',
            'total_deduction_amount': 'Nakit, sigorta, saha, önceki bakiye, ekipman ve benzeri kesintilerin toplam etkisini gösterir.',
            'kuryetec_bonus_tax_excluded': 'Kurye firmasının eklediği KDV hariç bonus tutarıdır.',
            'total_payment_tax_excluded': 'Bahşiş ve ana hakediş dahil, KDV hariç toplam ödeme tutarıdır.',
            'bonus_included_total_payment_tax_excluded': 'Kuryetec bonusu dahil edildikten sonra hesaplanan KDV hariç toplam ödeme tutarıdır.',
            'bonus_included_earning_tax_included': 'Bonus dahil hakedişin KDV dahil toplam tutarıdır.',
            'withholding_tax_amount': 'Fatura tipine göre hesaplanan tevkifat vergisi tutarıdır.',
            'net_payable_amount': 'Tüm kesintiler ve hesaplamalar sonrasında kuryeye ödenecek net tutardır.',
        }

    @http.route('/kurye-muhasebe', type='http', auth='public', website=True, sitemap=False)
    def login(self, **kw):
        if self._partner():
            return request.redirect('/kurye-muhasebe/home')
        return self._render('partner_courier_accounting.courier_accounting_login', {
            'error': kw.get('error'),
            'privacy_error': kw.get('privacy_error'),
        })

    @http.route('/kurye-muhasebe/login', type='http', auth='public', methods=['POST'], website=True, csrf=True, sitemap=False)
    def login_post(self, courier_id=None, identity_no=None, privacy_kvkk_accepted=None, **kw):
        courier_id = (courier_id or '').strip()
        identity_no = (identity_no or '').strip()
        partner = request.env['res.partner'].sudo().search([
            ('courier_id', '=', courier_id),
            ('courier_tc', '=', identity_no),
        ], limit=1)
        if not partner:
            return request.redirect('/kurye-muhasebe?error=1')
        if not partner.courier_privacy_kvkk_accepted:
            if privacy_kvkk_accepted != 'on':
                return request.redirect('/kurye-muhasebe?privacy_error=1')
            partner.write({
                'courier_privacy_kvkk_accepted': True,
                'courier_privacy_kvkk_accepted_at': fields.Datetime.now(),
            })
        request.session['courier_accounting_partner_id'] = partner.id
        return request.redirect('/kurye-muhasebe/home')

    @http.route('/kurye-muhasebe/logout', type='http', auth='public', website=True, sitemap=False)
    def logout(self, **kw):
        request.session.pop('courier_accounting_partner_id', None)
        return request.redirect('/kurye-muhasebe')

    @http.route('/kurye-muhasebe/admin/<int:partner_id>', type='http', auth='user', website=True, sitemap=False)
    def admin_open_partner_home(self, partner_id, **kw):
        partner = request.env['res.partner'].browse(partner_id).exists()
        if not partner:
            return request.redirect('/kurye-muhasebe')
        request.session['courier_accounting_partner_id'] = partner.id
        return request.redirect('/kurye-muhasebe/home')

    @http.route('/kurye-muhasebe/home', type='http', auth='public', website=True, sitemap=False)
    def home(self, **kw):
        partner = self._partner()
        if not partner:
            return request.redirect('/kurye-muhasebe')
        has_missing_documents = partner._has_missing_documents()
        user = partner.user_ids[:1]
        return self._render('partner_courier_accounting.courier_accounting_home', {
            'partner': partner,
            'has_missing_documents': has_missing_documents,
            'courier_user_id': user.id if user else False,
        })

    @http.route('/kurye-muhasebe/kisisel-bilgiler', type='http', auth='public', website=True, sitemap=False)
    def personal(self, **kw):
        partner = self._partner()
        if not partner:
            return request.redirect('/kurye-muhasebe')
        return self._render('partner_courier_accounting.courier_accounting_personal', {
            'partner': partner,
            'manager_phone_url': self._phone_url(partner.manager_phone),
        })

    @http.route('/kurye-muhasebe/iletisim-merkezleri', type='http', auth='public', website=True, sitemap=False)
    def contact_centers(self, **kw):
        partner = self._partner()
        if not partner:
            return request.redirect('/kurye-muhasebe')
        return self._render('partner_courier_accounting.courier_accounting_contact_centers', {
            'partner': partner,
            'centers': self._contact_centers(),
        })

    @http.route('/kurye-muhasebe/hakedis', type='http', auth='public', website=True, sitemap=False)
    def earnings(self, **kw):
        partner = self._partner()
        if not partner:
            return request.redirect('/kurye-muhasebe')
        lines = partner.courier_accounting_line_ids.filtered(lambda line: line.date_start and line.date_end)
        return self._render('partner_courier_accounting.courier_accounting_earnings', {
            'partner': partner,
            'lines': lines,
            'format_money': self._format_money,
            'format_date': self._format_date,
        })

    @http.route('/kurye-muhasebe/hakedis/<int:line_id>', type='http', auth='public', website=True, sitemap=False)
    def earning_detail(self, line_id, **kw):
        partner = self._partner()
        if not partner:
            return request.redirect('/kurye-muhasebe')
        line = request.env['partner.courier.accounting.line'].sudo().search([
            ('id', '=', line_id),
            ('partner_id', '=', partner.id),
        ], limit=1)
        if not line:
            return request.redirect('/kurye-muhasebe/hakedis')
        return self._render('partner_courier_accounting.courier_accounting_earning_detail', {
            'partner': partner,
            'line': line,
            'money': self._line_values(line),
            'info': self._line_descriptions(),
            'format_date': self._format_date,
        })

    @http.route('/kurye-muhasebe/hakedis/<int:line_id>/pdf', type='http', auth='public', website=True, sitemap=False)
    def earning_detail_pdf(self, line_id, **kw):
        partner = self._partner()
        if not partner:
            return request.redirect('/kurye-muhasebe')
        line = request.env['partner.courier.accounting.line'].sudo().search([
            ('id', '=', line_id),
            ('partner_id', '=', partner.id),
        ], limit=1)
        if not line:
            return request.redirect('/kurye-muhasebe/hakedis')

        pdf_content, _ = request.env['ir.actions.report'].sudo()._render_qweb_pdf(
            'partner_courier_accounting.action_report_courier_earning',
            [line.id]
        )
        start_str = line.date_start.strftime('%d_%m_%Y') if line.date_start else 'start'
        end_str = line.date_end.strftime('%d_%m_%Y') if line.date_end else 'end'
        filename = f"hakedis_{start_str}_{end_str}.pdf"

        download_token = (kw.get('download_token') or '').strip()
        pdfhttpheaders = [
            ('Content-Type', 'application/pdf'),
            ('Content-Length', len(pdf_content)),
            ('Content-Disposition', f'attachment; filename="{filename}"')
        ]
        response = request.make_response(pdf_content, headers=pdfhttpheaders)
        if download_token and len(download_token) <= 64 and download_token.replace('-', '').replace('_', '').isalnum():
            response.set_cookie(
                'courier_pdf_download_token',
                download_token,
                max_age=120,
                path='/',
                samesite='Lax',
            )
        return response

    @http.route('/kurye-muhasebe/belgeler', type='http', auth='public', website=True, sitemap=False)
    def documents(self, **kw):
        partner = self._partner()
        if not partner:
            return request.redirect('/kurye-muhasebe')
        return self._render('partner_courier_accounting.courier_accounting_documents', {
            'partner': partner,
            'error': kw.get('error'),
            'success': kw.get('success'),
        })

    @http.route('/kurye-muhasebe/egitimler', type='http', auth='public', website=True, sitemap=False)
    def trainings(self, **kw):
        partner = self._partner()
        if not partner:
            return request.redirect('/kurye-muhasebe')

        trainings = request.env['partner.courier.training'].sudo().search([
            ('active', '=', True),
        ])
        attendance_records = request.env['partner.courier.training.attendance'].sudo().search([
            ('partner_id', '=', partner.id),
            ('training_id', 'in', trainings.ids),
        ])
        attended_training_ids = set(attendance_records.mapped('training_id').ids)
        return self._render('partner_courier_accounting.courier_accounting_trainings', {
            'partner': partner,
            'trainings': trainings,
            'attended_training_ids': attended_training_ids,
        })

    @http.route('/kurye-muhasebe/egitimler/<int:training_id>', type='http', auth='public', website=True, sitemap=False)
    def training_detail(self, training_id, **kw):
        partner = self._partner()
        if not partner:
            return request.redirect('/kurye-muhasebe')

        training = self._training(training_id)
        if not training:
            return request.redirect('/kurye-muhasebe/egitimler')

        return self._render('partner_courier_accounting.courier_accounting_training_detail', {
            'partner': partner,
            'training': training,
            'has_attended': self._has_attended_training(training, partner),
            'success': kw.get('success'),
        })

    @http.route('/kurye-muhasebe/egitimler/<int:training_id>/katilim', type='http', auth='public', methods=['POST'], website=True, csrf=True, sitemap=False)
    def training_attend(self, training_id, **kw):
        partner = self._partner()
        if not partner:
            return request.redirect('/kurye-muhasebe')

        training = self._training(training_id)
        if not training:
            return request.redirect('/kurye-muhasebe/egitimler')

        attendance_model = request.env['partner.courier.training.attendance'].sudo()
        attendance = attendance_model.search([
            ('training_id', '=', training.id),
            ('partner_id', '=', partner.id),
        ], limit=1)
        if not attendance:
            attendance_model.create({
                'training_id': training.id,
                'partner_id': partner.id,
            })
        return request.redirect('/kurye-muhasebe/egitimler/%s?success=1' % training.id)

    @http.route('/kurye-muhasebe/egitimler/video/<int:training_id>', type='http', auth='public', website=True, sitemap=False)
    def training_video_file(self, training_id, **kw):
        partner = self._partner()
        if not partner:
            return request.redirect('/kurye-muhasebe')

        training = self._training(training_id)
        if not training or training.content_type != 'video_file' or not training.video_file:
            return request.not_found()

        stream = Stream.from_binary_field(training, 'video_file')
        if training.video_filename:
            stream.download_name = training.video_filename
            stream.mimetype = mimetypes.guess_type(training.video_filename)[0] or 'video/mp4'
        else:
            stream.mimetype = 'video/mp4'
        return stream.get_response(as_attachment=False)

    @http.route('/kurye-muhasebe/egitimler/dokuman/<int:training_id>/<int:attachment_id>', type='http', auth='public', website=True, sitemap=False)
    def training_document(self, training_id, attachment_id, **kw):
        partner = self._partner()
        if not partner:
            return request.redirect('/kurye-muhasebe')

        training = self._training(training_id)
        attachment = request.env['ir.attachment'].sudo().browse(attachment_id).exists()
        if not training or not attachment or attachment not in training.document_attachment_ids:
            return request.not_found()

        return Stream.from_attachment(attachment).get_response()

    @http.route('/kurye-muhasebe/belgeler/upload', type='http', auth='public', methods=['POST'], website=True, csrf=True, sitemap=False)
    def upload_document(self, doc_type=None, **kw):
        partner = self._partner()
        if not partner:
            return request.redirect('/kurye-muhasebe')
            
        valid_types = ['ehliyet', 'adli_sicil', 'p1_yetki', 'vergi_levhasi', 'src']
        if doc_type not in valid_types:
            return request.redirect('/kurye-muhasebe/belgeler?error=invalid_type')
            
        files = request.httprequest.files.getlist('files')
        if not files or all(f.filename == '' for f in files):
            return request.redirect('/kurye-muhasebe/belgeler?error=no_file')
            
        # Security validation: allowed extensions and size limit (5MB)
        allowed_extensions = {'.pdf', '.png', '.jpg', '.jpeg'}
        max_size = 5 * 1024 * 1024
        
        attachment_ids = []
        for file in files:
            if not file or file.filename == '':
                continue
            ext = os.path.splitext(file.filename)[1].lower()
            if ext not in allowed_extensions:
                return request.redirect('/kurye-muhasebe/belgeler?error=invalid_extension')
                
            data = file.read()
            if len(data) > max_size:
                return request.redirect('/kurye-muhasebe/belgeler?error=file_too_large')
                
            attachment = request.env['ir.attachment'].sudo().create({
                'name': file.filename,
                'type': 'binary',
                'datas': base64.b64encode(data),
                'res_model': 'res.partner',
                'res_id': partner.id,
            })
            attachment_ids.append(attachment.id)
            
        if attachment_ids:
            field_map = {
                'ehliyet': 'ehliyet_attachment',
                'adli_sicil': 'adli_sicil_attachment',
                'p1_yetki': 'p1_yetki_attachment',
                'vergi_levhasi': 'vergi_levhasi',
                'src': 'src_attachment'
            }
            field_name = field_map[doc_type]
            partner.sudo().write({
                field_name: [(4, att_id) for att_id in attachment_ids]
            })
            
        return request.redirect('/kurye-muhasebe/belgeler?success=1')

    @http.route('/kurye-muhasebe/talepler', type='http', auth='public', website=True, sitemap=False)
    def requests_list(self, **kw):
        partner = self._partner()
        if not partner:
            return request.redirect('/kurye-muhasebe')
            
        requests_records = request.env['partner.courier.request'].sudo().search([
            ('partner_id', '=', partner.id)
        ])
        
        state_labels = {
            'new': 'Yeni',
            'progress': 'İşleme Alındı',
            'approved': 'Onaylandı',
            'rejected': 'Reddedildi'
        }
        type_labels = {
            'advance': 'Avans Talebi',
            'equipment': 'Ekipman Talebi',
            'shift': 'Vardiya / Bölge Değişikliği',
            'holiday': 'İzin Talebi',
            'accounting': 'Hakediş İtirazı / Muhasebe',
            'other': 'Diğer'
        }
        
        return self._render('partner_courier_accounting.courier_accounting_requests', {
            'partner': partner,
            'requests': requests_records,
            'state_labels': state_labels,
            'type_labels': type_labels,
            'format_date': self._format_date,
            'success': kw.get('success'),
        })

    @http.route('/kurye-muhasebe/talepler/yeni', type='http', auth='public', website=True, sitemap=False)
    def new_request(self, **kw):
        partner = self._partner()
        if not partner:
            return request.redirect('/kurye-muhasebe')
            
        type_labels = [
            ('advance', 'Avans Talebi'),
            ('equipment', 'Ekipman Talebi'),
            ('shift', 'Vardiya / Bölge Değişikliği'),
            ('holiday', 'İzin Talebi'),
            ('accounting', 'Hakediş İtirazı / Muhasebe'),
            ('other', 'Diğer')
        ]
        
        return self._render('partner_courier_accounting.courier_accounting_new_request', {
            'partner': partner,
            'type_labels': type_labels,
            'error': kw.get('error'),
        })

    @http.route('/kurye-muhasebe/talepler/yeni/post', type='http', auth='public', methods=['POST'], website=True, csrf=True, sitemap=False)
    def create_request(self, type=None, description=None, requested_amount=None, **kw):
        partner = self._partner()
        if not partner:
            return request.redirect('/kurye-muhasebe')
            
        type_val = (type or '').strip()
        desc_val = (description or '').strip()
        amount_val = self._parse_amount(requested_amount)
        
        valid_types = ['advance', 'equipment', 'shift', 'holiday', 'accounting', 'other']
        if not type_val or type_val not in valid_types or not desc_val or (type_val == 'advance' and amount_val <= 0):
            return request.redirect('/kurye-muhasebe/talepler/yeni?error=1')
            
        request.env['partner.courier.request'].sudo().create({
            'partner_id': partner.id,
            'type': type_val,
            'requested_amount': amount_val if type_val == 'advance' else 0.0,
            'description': desc_val,
            'state': 'new',
        })
        
        return request.redirect('/kurye-muhasebe/talepler?success=1')

    @http.route('/kurye-muhasebe/belgeler/indir/<int:attachment_id>', type='http', auth='public', website=True, sitemap=False)
    def download_document(self, attachment_id, **kw):
        partner = self._partner()
        if not partner:
            return request.redirect('/kurye-muhasebe')
            
        attachment = request.env['ir.attachment'].sudo().browse(attachment_id)
        if not attachment.exists():
            return request.not_found()
            
        # Verify ownership: check if the attachment belongs to this partner
        _logger.info("DOWNLOADING ATTACHMENT: partner_id=%s, attachment_id=%s", partner.id, attachment_id)
        _logger.info("attachment res_model=%s, res_id=%s", attachment.res_model, attachment.res_id)
        _logger.info("partner fields: ehliyet=%s, adli_sicil=%s, p1_yetki=%s, vergi_levhasi=%s, src=%s",
                     partner.ehliyet_attachment.ids, partner.adli_sicil_attachment.ids,
                     partner.p1_yetki_attachment.ids, partner.vergi_levhasi.ids, partner.src_attachment.ids)
        is_owner = (
            (attachment.res_model == 'res.partner' and attachment.res_id == partner.id) or
            attachment_id in partner.ehliyet_attachment.ids or
            attachment_id in partner.adli_sicil_attachment.ids or
            attachment_id in partner.p1_yetki_attachment.ids or
            attachment_id in partner.vergi_levhasi.ids or
            attachment_id in partner.src_attachment.ids
        )
        _logger.info("is_owner result: %s", is_owner)
        if not is_owner:
            return request.render('http_routing.403')
            
        return Stream.from_attachment(attachment).get_response()

    @http.route('/kurye-muhasebe/belgeler/sil/<int:attachment_id>', type='http', auth='public', website=True, sitemap=False)
    def delete_document(self, attachment_id, **kw):
        partner = self._partner()
        if not partner:
            return request.redirect('/kurye-muhasebe')
            
        attachment = request.env['ir.attachment'].sudo().browse(attachment_id)
        if not attachment.exists():
            return request.not_found()
            
        # Verify ownership: check if the attachment belongs to this partner
        is_owner = (
            (attachment.res_model == 'res.partner' and attachment.res_id == partner.id) or
            attachment_id in partner.ehliyet_attachment.ids or
            attachment_id in partner.adli_sicil_attachment.ids or
            attachment_id in partner.p1_yetki_attachment.ids or
            attachment_id in partner.vergi_levhasi.ids or
            attachment_id in partner.src_attachment.ids
        )
        if not is_owner:
            return request.render('http_routing.403')
            
        # Check time window: 5 minutes limit
        if not attachment.is_deletable_by_courier():
            return request.redirect('/kurye-muhasebe/belgeler?error=timeout')
            
        # Unlink the attachment
        attachment.unlink()
        return request.redirect('/kurye-muhasebe/belgeler?success=2')
