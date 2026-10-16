import json
from datetime import datetime, timedelta

from odoo import fields, http, _
from odoo.http import request
from odoo.tools.misc import get_lang
from werkzeug.exceptions import NotFound


class PartnerCourierCallController(http.Controller):

    def _get_courier(self):
        partner_id = request.session.get('courier_accounting_partner_id')
        if not partner_id:
            return request.env['res.partner']
        courier = request.env['res.partner'].sudo().browse(partner_id).exists()
        if not courier or not courier.active or not courier.courier_id:
            request.session.pop('courier_accounting_partner_id', None)
            return request.env['res.partner']
        return courier

    @http.route(
        '/kurye-gorusme/baslat',
        type='http',
        auth='public',
        methods=['POST'],
        website=True,
        csrf=True,
        sitemap=False,
    )
    def start_call(self, target=None, **post):
        courier = self._get_courier()
        if not courier:
            return request.redirect('/kurye-muhasebe')
        if target not in ('field_manager', 'support'):
            return request.redirect('/kurye-muhasebe/home?call_error=invalid_target')

        Call = request.env['partner.courier.call'].sudo()
        call = Call.search([
            ('courier_id', '=', courier.id),
            ('state', 'in', ['waiting', 'ringing']),
            ('expires_at', '>', fields.Datetime.now()),
        ], order='create_date desc', limit=1)
        if call:
            return request.redirect('/kurye-gorusme/%s' % call.access_token)

        if target == 'support':
            if not Call.is_support_hours_open():
                return request.redirect('/kurye-muhasebe/home?call_error=support_closed')
            manager = Call.get_available_support_partner()
            if not manager:
                return request.redirect('/kurye-muhasebe/home?call_error=support_unavailable')
        else:
            manager = courier.courier_field_manager_partner_id
            if not manager and courier.courier_field_manager_id:
                manager = courier.courier_field_manager_id.partner_id
            if not manager or not manager.active or manager == courier:
                return request.redirect('/kurye-muhasebe/home?call_error=manager_missing')

        call = Call.create_courier_call(courier, manager_partner=manager)
        if target == 'support':
            manager.sudo().write({'courier_call_support_last_call_at': fields.Datetime.now()})
        call.schedule_manager_notification()
        return request.redirect('/kurye-gorusme/%s' % call.access_token)

    def _render_guest_call(self, call, guest_field, guest_name, counterpart_name, exit_url, call_token):
        if guest_field == 'manager_guest_id':
            call._prepare_manager_guest_join()
        guest = call[guest_field].sudo().exists()
        if not guest:
            country_code = request.geoip.get('country_code') if request.geoip else False
            guest = request.env['mail.guest'].sudo().create({
                'country_id': request.env['res.country'].sudo().search([
                    ('code', '=', country_code),
                ], limit=1).id if country_code else False,
                'lang': get_lang(request.env).code,
                'name': guest_name,
                'timezone': request.env['mail.guest']._get_timezone_from_request(request),
            })
            call.write({guest_field: guest.id})

        channel = call.channel_id.sudo().with_context(guest=guest)
        data = {
            'channelData': channel.channel_info()[0],
            'discussPublicViewData': {
                'channel': [('insert', {'id': channel.id, 'model': 'mail.channel'})],
                'isChannelTokenSecret': True,
                'shouldAddGuestAsMemberOnJoin': True,
                'shouldDisplayWelcomeViewInitially': True,
                'startAudioOnly': True,
            },
        }
        response = request.render('partner_courier_call.courier_call_public_template', {
            'call_config': {
                'endUrl': '/kurye-gorusme/sonlandir/%s' % call_token,
                'exitUrl': exit_url,
                'statusUrl': '/kurye-gorusme/durum/%s' % call_token,
            },
            'counterpart_name': counterpart_name,
            'data': data,
            'exit_url': exit_url,
            'json': json,
            'session_info': channel.env['ir.http'].session_info(),
            'title': _('Kuryetec Görüşme'),
        })
        expiration_date = datetime.now() + timedelta(days=1)
        response.set_cookie(
            guest._cookie_name,
            '%s%s%s' % (guest.id, guest._cookie_separator, guest.access_token),
            httponly=True,
            secure=request.httprequest.scheme == 'https',
            samesite='Lax',
            expires=expiration_date,
        )
        return response

    @http.route(
        '/kurye-gorusme/<string:access_token>',
        type='http',
        auth='public',
        methods=['GET'],
        website=False,
        csrf=False,
        sitemap=False,
    )
    def open_call(self, access_token, **kwargs):
        courier = self._get_courier()
        if not courier:
            return request.redirect('/kurye-muhasebe')

        call = request.env['partner.courier.call'].sudo().search([
            ('access_token', '=', access_token),
            ('courier_id', '=', courier.id),
            ('state', 'in', ['waiting', 'ringing', 'active']),
        ], limit=1)
        if not call or call.expires_at < fields.Datetime.now() or not call.channel_id:
            return request.redirect('/kurye-muhasebe/home?call_error=expired')

        return self._render_guest_call(
            call,
            'guest_id',
            courier.name,
            call._manager_partner().name,
            '/kurye-muhasebe/home',
            call.access_token,
        )

    @http.route(
        '/kurye-gorusme/yonetici/<string:manager_access_token>',
        type='http',
        auth='public',
        methods=['GET'],
        website=True,
        csrf=False,
        sitemap=False,
    )
    def open_manager_call(self, manager_access_token, **kwargs):
        call = request.env['partner.courier.call'].sudo().search([
            ('manager_access_token', '=', manager_access_token),
        ], limit=1)
        if not call:
            raise NotFound()
        if (
            call.state not in ['waiting', 'ringing', 'active']
            or call.expires_at < fields.Datetime.now()
            or not call.channel_id
        ):
            return self._render_manager_call_closed(call)

        return self._render_guest_call(
            call,
            'manager_guest_id',
            call._manager_partner().name,
            call.courier_id.name,
            '/kurye-muhasebe/home',
            call.manager_access_token,
        )

    def _render_manager_call_closed(self, call):
        caller_name = call._caller_display_name()
        if call.ended_by == 'courier':
            message = _('%s görüşmeden çıktı.') % caller_name
        elif call.state == 'rejected':
            message = _('Bu arama reddedildi.')
        elif call.state == 'missed':
            message = _('Bu arama cevaplanmadan sona erdi.')
        elif call.state == 'expired' or call.expires_at < fields.Datetime.now():
            message = _('Bu aramanın bağlantı süresi doldu.')
        else:
            message = _('Bu görüşme sona erdi.')
        return request.render('partner_courier_call.courier_call_closed_template', {
            'caller_name': caller_name,
            'message': message,
        })

    @http.route(
        '/kurye-gorusme/yonetici/<string:manager_access_token>/reddet',
        type='http',
        auth='public',
        methods=['GET'],
        website=True,
        csrf=False,
        sitemap=False,
    )
    def reject_manager_call(self, manager_access_token, **kwargs):
        call = request.env['partner.courier.call'].sudo().search([
            ('manager_access_token', '=', manager_access_token),
        ], limit=1)
        if not call:
            raise NotFound()

        rejected = call.action_reject_call()
        return request.render('partner_courier_call.courier_call_rejected_template', {
            'caller_name': call._caller_display_name(),
            'rejected': rejected or call.state == 'rejected',
        })

    def _get_call_by_token(self, call_token):
        return request.env['partner.courier.call'].sudo().search([
            '|',
            ('access_token', '=', call_token),
            ('manager_access_token', '=', call_token),
        ], limit=1)

    @http.route(
        '/kurye-gorusme/durum/<string:call_token>',
        type='http',
        auth='public',
        methods=['GET'],
        website=False,
        csrf=False,
        sitemap=False,
    )
    def call_status(self, call_token, **kwargs):
        call = self._get_call_by_token(call_token)
        if not call:
            raise NotFound()
        payload = {
            'open': bool(call.channel_id and call.state in ['waiting', 'ringing', 'active']),
            'state': call.state,
        }
        return request.make_response(
            json.dumps(payload),
            headers=[('Content-Type', 'application/json; charset=utf-8')],
        )

    @http.route(
        '/kurye-gorusme/sonlandir/<string:call_token>',
        type='http',
        auth='public',
        methods=['POST'],
        website=False,
        csrf=False,
        sitemap=False,
    )
    def end_call(self, call_token, **post):
        call = self._get_call_by_token(call_token)
        if not call:
            raise NotFound()
        ended_by = 'courier' if call.access_token == call_token else 'manager'
        call.action_end_call(ended_by=ended_by)
        return request.make_response(
            json.dumps({'ended': True, 'state': call.state}),
            headers=[('Content-Type', 'application/json; charset=utf-8')],
        )

    @http.route(
        '/kurye-gorusme/<string:access_token>/iptal',
        type='http',
        auth='public',
        methods=['POST'],
        website=True,
        csrf=True,
        sitemap=False,
    )
    def cancel_call(self, access_token, **post):
        courier = self._get_courier()
        if not courier:
            raise NotFound()
        call = request.env['partner.courier.call'].sudo().search([
            ('access_token', '=', access_token),
            ('courier_id', '=', courier.id),
            ('state', 'in', ['waiting', 'ringing']),
        ], limit=1)
        if call:
            call.write({
                'state': 'cancelled',
                'ended_at': fields.Datetime.now(),
                'ended_by': 'courier',
            })
        return request.redirect('/kurye-muhasebe/home')
