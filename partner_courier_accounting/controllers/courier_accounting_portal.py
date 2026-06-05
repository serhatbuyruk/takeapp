import base64
import os
from odoo import http
from odoo.http import request


class CourierAccountingPortal(http.Controller):

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

    def _format_date(self, value):
        return value.strftime('%d/%m/%Y') if value else ''

    def _line_values(self, line):
        currency = line.currency_id or request.env.company.currency_id
        money_fields = [
            'pickup_amount', 'dropoff_amount', 'distance_amount', 'weekly_extra_package_amount',
            'tip_amount_tax_excluded', 'cash_deduction_tax_included', 'softpos_deduction_tax_included',
            'insurance_deduction_amount', 'ixopay_cash_deposit_amount', 'total_deduction_amount',
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
            'insurance_deduction_amount': 'İlgili hafta için uygulanan sigorta kesintisi tutarıdır.',
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
        return self._render('partner_courier_accounting.courier_accounting_login', {'error': kw.get('error')})

    @http.route('/kurye-muhasebe/login', type='http', auth='public', methods=['POST'], website=True, csrf=True, sitemap=False)
    def login_post(self, courier_id=None, identity_no=None, **kw):
        courier_id = (courier_id or '').strip()
        identity_no = (identity_no or '').strip()
        partner = request.env['res.partner'].sudo().search([
            ('courier_id', '=', courier_id),
            '|',
            ('invoice_person_tc', '=', identity_no),
            ('payment_person_tc', '=', identity_no),
        ], limit=1)
        if not partner:
            return request.redirect('/kurye-muhasebe?error=1')
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
        return self._render('partner_courier_accounting.courier_accounting_home', {
            'partner': partner,
            'has_missing_documents': has_missing_documents,
        })

    @http.route('/kurye-muhasebe/kisisel-bilgiler', type='http', auth='public', website=True, sitemap=False)
    def personal(self, **kw):
        partner = self._partner()
        if not partner:
            return request.redirect('/kurye-muhasebe')
        return self._render('partner_courier_accounting.courier_accounting_personal', {'partner': partner})

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
    def create_request(self, type=None, description=None, **kw):
        partner = self._partner()
        if not partner:
            return request.redirect('/kurye-muhasebe')
            
        type_val = (type or '').strip()
        desc_val = (description or '').strip()
        
        valid_types = ['advance', 'equipment', 'shift', 'holiday', 'accounting', 'other']
        if not type_val or type_val not in valid_types or not desc_val:
            return request.redirect('/kurye-muhasebe/talepler/yeni?error=1')
            
        request.env['partner.courier.request'].sudo().create({
            'partner_id': partner.id,
            'type': type_val,
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
        is_owner = (
            attachment in partner.ehliyet_attachment or
            attachment in partner.adli_sicil_attachment or
            attachment in partner.p1_yetki_attachment or
            attachment in partner.vergi_levhasi or
            attachment in partner.src_attachment
        )
        if not is_owner:
            return request.render('website.403')
            
        status, headers, content = request.env['ir.http'].binary_content(
            id=attachment.id,
            model='ir.attachment',
            field='datas',
            download=False
        )
        if status == 304:
            return request.make_response(b'', headers, status=304)
        elif status == 404:
            return request.not_found()
            
        content = base64.b64decode(content)
        headers = dict(headers)
        headers['Content-Length'] = len(content)
        return request.make_response(content, list(headers.items()))

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
            attachment in partner.ehliyet_attachment or
            attachment in partner.adli_sicil_attachment or
            attachment in partner.p1_yetki_attachment or
            attachment in partner.vergi_levhasi or
            attachment in partner.src_attachment
        )
        if not is_owner:
            return request.render('website.403')
            
        # Check time window: 5 minutes limit
        if not attachment.is_deletable_by_courier():
            return request.redirect('/kurye-muhasebe/belgeler?error=timeout')
            
        # Unlink the attachment
        attachment.unlink()
        return request.redirect('/kurye-muhasebe/belgeler?success=2')
