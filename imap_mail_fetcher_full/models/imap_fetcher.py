from odoo import models, fields, api
import logging
import imaplib
import email
from email.header import decode_header
from email.utils import parsedate_to_datetime
import datetime
import re

_logger = logging.getLogger(__name__)

class MailFetcherRun(models.Model):
    _name = 'imap.mail.fetcher.run'
    _description = 'IMAP Manual Trigger'

    name = fields.Char(default="Yeni Mail Kontrolü", readonly=True)
    state = fields.Selection([('draft', 'Taslak'), ('done', 'Tamamlandı')], default='draft')

    def action_fetch_mail(self):
        _logger.info("🟡 [MANUEL] Yeni mail kontrolü başlatıldı.")
        self.env['imap.mail.fetcher'].fetch_new_emails()
        self.write({'state': 'done'})


class MailFetcher(models.Model):
    _name = 'imap.mail.fetcher'
    _description = 'IMAP Mail Fetcher'
    

    @api.model
    def fetch_new_emails(self):
        _logger.info("⏳ Otomatik IMAP kontrol başlatıldı...")
        servers = self.env['fetchmail.server'].search([
            ('active', '=', True),
            ('server_type', '=', 'imap')
        ])

        for server in servers:
            try:
                _logger.info(f"📦 fetchmail.server '{server.name}' alanları:")
                for field in server._fields:
                    value = getattr(server, field, None)
                    _logger.info(f"     🔹 {field} = {value}")

                host = server.server
                port = server.port
                username = server.user
                password = server.password
                ssl = getattr(server, 'is_ssl', False)

                _logger.info(f"🔗 Bağlantı kuruluyor → {host}:{port} | SSL: {ssl}")
                mail = imaplib.IMAP4_SSL(host, port) if ssl else imaplib.IMAP4(host, port)
                mail.login(username, password)
                _logger.info("🔐 SSL bağlantısı başlatıldı.")

                mail.select("inbox")
                result, data = mail.search(None, 'UNSEEN')
                mail_ids = data[0].split()

                _logger.info(f"📬 {server.name} sunucusunda {len(mail_ids)} yeni mail bulundu.")
                for mail_id in mail_ids:
                    result, msg_data = mail.fetch(mail_id, '(RFC822)')
                    raw_email = msg_data[0][1]
                    msg = email.message_from_bytes(raw_email)
                    
                    mail.store(mail_id, '+FLAGS', '\\Seen')

                    subject, encoding = decode_header(msg["Subject"])[0]
                    if isinstance(subject, bytes):
                        subject = subject.decode(encoding or 'utf-8', errors='ignore')

                    sender = msg.get("From")
                    date_str = msg.get("Date")
                    
                    if "camsender@devlabs.com.tr" in sender: 
                    
                        try:
                            mail_date = parsedate_to_datetime(date_str)
                            if mail_date and mail_date.tzinfo:
                                mail_date = mail_date.replace(tzinfo=None)
                        except:
                            mail_date = fields.Datetime.now()

                        body = ""
                        if msg.is_multipart():
                            for part in msg.walk():
                                if part.get_content_type() == "text/plain" and part.get_payload(decode=True):
                                    body = part.get_payload(decode=True).decode(errors='ignore')
                                    break
                        else:
                            body = msg.get_payload(decode=True).decode(errors='ignore')

                        clean_body = body.replace('\x00', '')

                        _logger.info(f"📨 Yeni mail alındı: {subject} | Gönderen: {sender}")
                        self.env['imap.mail.log'].create({
                            'subject': subject,
                            'sender': sender,
                            'body': clean_body,
                            'mail_date': mail_date,
                            'server_id': server.id,
                        })
                    else:
                        _logger.info(f"📨 İlgili olmayan mail atlandı: {subject} | Gönderen: {sender}")
                        False    
                        
                        
                    

                mail.logout()

            except Exception as e:
                _logger.error(f"❌ HATA → {server.name} sunucusunda hata oluştu: {str(e)}")


class ImapMailLog(models.Model):
    _name = 'imap.mail.log'
    _description = 'Fetched Mail Log'
    
    name = fields.Char(default="Yeni Mail")

    subject = fields.Char(string="Subject")
    sender = fields.Char(string="Sender")
    body = fields.Text(string="Body")
    mail_date = fields.Datetime(string="Mail Date")
    server_id = fields.Many2one('fetchmail.server', string="Sunucu")

    event_type = fields.Char(string="Event Type")
    event_time = fields.Datetime(string="Event Time")
    alarm_start_time = fields.Datetime(string="Alarm Start Time")
    alarm_stop_time = fields.Datetime(string="Alarm Stop Time")
    ipc_name = fields.Char(string="IPC Name")
    ipc_sn = fields.Char(string="IPC Serial No")
    ip_address = fields.Char(string="IP Address")
    zone = fields.Char(string="Zone")

    @staticmethod
    def parse_alarm_email_simple_unv(body):
        data = {}
        for line in body.splitlines():
            if line.upper().startswith("EVENT TYPE:"):
                data['event_type'] = line.split(":", 1)[1].strip()
            elif line.upper().startswith("IPC S/N:"):
                data['ipc_sn'] = line.split(":", 1)[1].strip()
            elif line.upper().startswith("IPC NAME:"):
                data['ipc_name'] = line.split(":", 1)[1].strip()
            elif line.upper().startswith("EVENT TIME:"):
                try:
                    date_str = line.split(":", 1)[1].strip()
                    if date_str:
                        data['event_time'] = datetime.datetime.strptime(date_str, "%Y-%m-%d,%H:%M:%S")
                    else:
                        data['event_time'] = ""
                except Exception as e:
                    data['event_time'] = ""

        #data['name'] = f"{subject} - {data.get('event_type', '')}" 
        data['name'] = f"{data.get('event_type', '')} - {data.get('ipc_name', '')}"    
        return data
        
    @staticmethod
    def parse_alarm_email_simple_dahua(body):
        data = {}
        for line in body.splitlines():
            line_upper = line.upper().strip()

            if line_upper.startswith("ALARM EVENT:"):
                data['event_type'] = line.split(":", 1)[1].strip()

            elif line_upper.startswith("ALARM INPUT CHANNEL:"):
                data['zone'] = line.split(":", 1)[1].strip()

            elif line_upper.startswith("ALARM DEVICE NAME:"):
                data['ipc_sn'] = line.split(":", 1)[1].strip()

            elif line_upper.startswith("ALARM NAME:"):
                data['ipc_name'] = line.split(":", 1)[1].strip()

            elif "ALARM START TIME" in line_upper:
                match = re.search(r'(\d{2}/\d{2}/\d{4} \d{2}:\d{2}:\d{2})', line)
                if match:
                    try:
                        data['alarm_start_time'] = datetime.datetime.strptime(match.group(1), "%d/%m/%Y %H:%M:%S")
                    except Exception as e:
                        _logger.warning("❌ Alarm START TIME ayrıştırılamadı: %s", e)
                        data['alarm_start_time'] = ""
                else:
                    data['alarm_start_time'] = ""

            elif "ALARM STOP TIME" in line_upper:
                match = re.search(r'(\d{2}/\d{2}/\d{4} \d{2}:\d{2}:\d{2})', line)
                if match:
                    try:
                        data['alarm_stop_time'] = datetime.datetime.strptime(match.group(1), "%d/%m/%Y %H:%M:%S")
                    except Exception as e:
                        _logger.warning("❌ Alarm STOP TIME ayrıştırılamadı: %s", e)
                        data['alarm_stop_time'] = ""
                else:
                    data['alarm_stop_time'] = ""

            elif line_upper.startswith("IP ADDRESS:"):
                data['ip_address'] = line.split(":", 1)[1].strip()
        data['name'] = f"{data.get('event_type', '')} - {data.get('ipc_name', '')}"    
        return data
    
 

    @staticmethod
    def parse_alarm_email_health_test(body):
        data = {}
        for line in body.splitlines():
            clean_line = line.strip().upper()

            if clean_line.startswith("ALARM EVENT:"):
                data['event_type'] = line.split(":", 1)[1].strip()

            elif clean_line.startswith("ALARM INPUT CHANNEL:"):
                data['zone'] = line.split(":", 1)[1].strip()

            elif clean_line.startswith("ALARM DEVICE NAME:"):
                data['ipc_sn'] = line.split(":", 1)[1].strip()

            elif clean_line.startswith("ALARM NAME:"):
                data['ipc_name'] = line.split(":", 1)[1].strip()

            elif "ALARM START TIME" in clean_line:
                match = re.search(r'(\d{2}/\d{2}/\d{4} \d{2}:\d{2}:\d{2})', line)
                if match:
                    try:
                        data['event_time'] = datetime.datetime.strptime(match.group(1), "%d/%m/%Y %H:%M:%S")
                    except Exception as e:
                        _logger.warning("⚠️ Health test tarihi ayrıştırılamadı: %s", e)
                        data['event_time'] = ""
                else:
                    data['event_time'] = ""

            elif clean_line.startswith("IP ADDRESS:"):
                data['ip_address'] = line.split(":", 1)[1].strip()
        
        data['name'] = f"{data.get('event_type', '')} - {data.get('ipc_name', '')}"    
        return data





     

    @staticmethod
    def parse_by_subject(subject, body):
        return ImapMailLog.parse_alarm_email_simple_unv(body)

    @api.model
    def create(self, vals):
        body = vals.get('body') or ''
        subject = vals.get('subject') or ''
        sender = vals.get('sender') or ''

        if body:
            if 'dahua' in subject.lower():
                _logger.warning("⚠️ dahua alarm türü: %s", subject)
                parsed_data = self.parse_alarm_email_simple_dahua(body)
                vals.update(parsed_data)
            elif 'unv' in subject.lower():
                _logger.warning("⚠️ unv alarm türü: %s", subject)
                parsed_data = self.parse_alarm_email_simple_unv(body)
                vals.update(parsed_data)
            elif 'health' in subject.lower():
                _logger.warning("⚠️ health alarm türü: %s", subject)
                parsed_data = self.parse_alarm_email_health_test(body)
                vals.update(parsed_data)
            else:
                _logger.warning("⚠️ Bilinmeyen alarm türü: %s", subject)

        # Tekrar eden mail kontrolü – son 5 dk içinde aynı cihazdan (ipc_sn), aynı event_type veya subject varsa oluşturma
        now = fields.Datetime.now()
        five_minutes_ago = now - datetime.timedelta(minutes=5) + datetime.timedelta(hours=3)  # Türkiye saati için UTC+3 ekleniyor
        
        _logger.info("⛔ five_minutes_ago: %s ", five_minutes_ago)

        duplicate_domain = [
            ('sender', '=', sender),
            ('ipc_sn', '=', vals.get('ipc_sn')),
            '|',
            ('event_type', '=', vals.get('event_type')),
            ('subject', '=', subject),
            ('create_date', '>=', five_minutes_ago)
        ]

        if self.search_count(duplicate_domain):
            _logger.info("⛔ Duplicate alarm skipped (subject/event_type): %s - %s", subject, vals.get('ipc_sn'))
            return False

        return super().create(vals)
