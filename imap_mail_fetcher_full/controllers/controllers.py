from odoo import http, fields
from odoo.http import request
import json
import datetime
import logging
import re

_logger = logging.getLogger('odoo.addons.imap_mail_fetcher_full.controllers.mail_callback')

class imapMailLogReq(http.Controller):

    @http.route('/mail-callback', type="json", auth="public", methods=["POST"], cors='*', csrf=False)
    def yeppos_order(self):
        _logger.info("📬 Mail callback endpoint çağrıldı.")
        try:
            _logger.info("📥 Gelen veri: %s", request.httprequest.data)
            data = json.loads(request.httprequest.data)

            subject = data.get("subject", "")
            _logger.info("📧 Mail konusu: %s", subject)
            sender = data.get("sender", "")
            _logger.info("📤 Mail gönderen: %s", sender)
            mailbody = data.get("mailbody", "")
            _logger.info("📜 Mail içeriği: %s", mailbody[:100] + "...")  # İlk 100 karakteri logla
            date_str = data.get("date", "")
            _logger.info("📅 Mail tarihi: %s", date_str)
            
            # Mail tarihi
            try:
                mail_date = datetime.datetime.fromisoformat(date_str.replace("Z", ""))
            except:
                mail_date = fields.Datetime.now()

            _logger.info("📩 Yeni mail alındı: %s | Gönderen: %s", subject, sender)

            lowered_subject = subject.lower()
            parsed_data = {}

            if "unv" in lowered_subject:
                _logger.info("📡 UNV alarm maili işleniyor.")
                parsed_data = request.env['imap.mail.log'].parse_alarm_email_simple_unv(mailbody)
            elif "health" in lowered_subject:
                _logger.info("💓 Health Test alarm maili işleniyor.")
                parsed_data = request.env['imap.mail.log'].parse_alarm_email_health_test(mailbody)
            elif "dahua" in lowered_subject or "alarm event" in mailbody.lower():
                _logger.info("📡 Dahua alarm maili işleniyor.")
                parsed_data = request.env['imap.mail.log'].parse_alarm_email_simple_dahua(mailbody)
            else:
                _logger.warning("⚠️ Bilinmeyen alarm formatı: %s", subject)

            name = f"{subject} - {parsed_data.get('event_type', '')}"

            created_record = request.env['imap.mail.log'].sudo().create({
                'subject': subject,
                'sender': sender,
                'body': mailbody,
                'mail_date': mail_date,
                'event_type': parsed_data.get('event_type'),
                'event_time': parsed_data.get('event_time'),
                'alarm_start_time': parsed_data.get('alarm_start_time'),
                'alarm_stop_time': parsed_data.get('alarm_stop_time'),
                'ipc_name': parsed_data.get('ipc_name'),
                'ipc_sn': parsed_data.get('ipc_sn'),
                'ip_address': parsed_data.get('ip_address'),
                'zone': parsed_data.get('zone'),
                'name': name,
            })

            _logger.info("✅ Mail başarıyla işlendi ve kayıt oluşturuldu: %s", created_record.id)
            return {"status": "success", "id": created_record.id, "subject": subject}

        except Exception as e:
            _logger.exception("❌ Callback mail işleme hatası: %s", str(e))
            return {"error": str(e)}
