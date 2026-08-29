from odoo import _, fields, http
from odoo.exceptions import AccessError, UserError, ValidationError
from odoo.http import request


class CourierPackageReconciliationController(http.Controller):

    @staticmethod
    def _local_datetime(value, date_only=False):
        if not value:
            return ''
        localized = fields.Datetime.context_timestamp(request.env.user, value)
        return localized.strftime('%d.%m.%Y' if date_only else '%d.%m.%Y %H:%M')

    @http.route(
        '/courier/package-reconciliation/pending',
        type='json',
        auth='user',
        methods=['POST'],
        website=True,
    )
    def pending_package_reconciliation(self):
        courier = request.env.user.partner_id
        if courier.user_role != 'kurye':
            return {'required': False}
        line = request.env['skurye.profile.lines'].sudo(
        ).get_pending_courier_declaration(courier)
        if not line:
            return {'required': False}
        slot = line._package_reconciliation_slot()
        effective_end = line._package_reconciliation_effective_end(slot)
        return {
            'required': True,
            'line_id': line.id,
            'slot_name': slot.name or _('Sabit Kurye Vardiyası'),
            'restaurant_name': slot.magazalar[:1].name or '',
            'slot_date': self._local_datetime(slot.start_date, date_only=True),
            'time_range': '%s – %s' % (
                self._local_datetime(line.kurye_start_date or slot.start_date)[-5:],
                self._local_datetime(effective_end)[-5:],
            ),
        }

    @http.route(
        '/courier/package-reconciliation/submit',
        type='json',
        auth='user',
        methods=['POST'],
        website=True,
    )
    def submit_package_reconciliation(self, line_id=None, package_count=None):
        courier = request.env.user.partner_id
        try:
            normalized_line_id = int(line_id or 0)
        except (TypeError, ValueError):
            normalized_line_id = 0
        line = request.env['skurye.profile.lines'].sudo().browse(
            normalized_line_id
        ).exists()
        if not line:
            return {'status': 'error', 'message': _('Vardiya kaydı bulunamadı.')}
        try:
            line.submit_courier_package_count(courier, package_count)
        except (AccessError, UserError, ValidationError) as error:
            return {
                'status': 'error',
                'message': error.args[0] if error.args else str(error),
            }
        return {
            'status': 'success',
            'message': _('Paket sayınız restoran onayına gönderildi.'),
        }

    @http.route(
        '/paket-sayilari',
        type='http',
        auth='user',
        methods=['GET'],
        website=True,
        sitemap=False,
    )
    def courier_package_counts(self, **kwargs):
        courier = request.env.user.partner_id
        if courier.user_role != 'kurye':
            return request.redirect('/')
        lines = request.env['skurye.profile.lines'].sudo().search([
            ('partner_id', '=', courier.id),
            ('kurye_paket_beyani_yapildi', '=', True),
        ], order='kurye_paket_beyan_zamani desc, id desc', limit=250)
        status_labels = {
            'pending': _('Restoran Onayı Bekleniyor'),
            'approved': _('Restoran Onayladı'),
            'rejected': _('Restoran Reddetti'),
            'auto_approved': _('Otomatik Onaylandı'),
        }
        records = []
        for line in lines:
            slot = line.paket_mutabakat_slot_id
            records.append({
                'slot_name': slot.name or _('Sabit Kurye Vardiyası'),
                'restaurant_name': line.paket_mutabakat_restoran_id.name or '',
                'slot_date': self._local_datetime(slot.start_date, date_only=True),
                'package_count': line.kurye_beyan_paket_sayisi,
                'state': line.paket_mutabakat_durumu,
                'state_label': status_labels.get(
                    line.paket_mutabakat_durumu,
                    line.paket_mutabakat_durumu,
                ),
                'submitted_at': self._local_datetime(
                    line.kurye_paket_beyan_zamani
                ),
            })
        return request.render(
            'kuryetec_website.courier_package_counts_page',
            {'package_records': records},
        )
