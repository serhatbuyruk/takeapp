# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
import requests
import json
import re
import logging
from datetime import datetime, timedelta
from base64 import b64encode
import time
_logger = logging.getLogger(__name__)
DEEPL_API_TIMEOUT = 20  # Timeout in seconds for API calls


class TranslationProfileLines(models.Model):
    _name = 'translation.profile.lines'
    _description = 'Translation Lines Record'
    _order = 'id'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    # 1. Alan İyileştirmeleri
    name = fields.Char("Name", index=True)
    lang = fields.Many2one(
        'res.lang',
        string='Language',
        required=True,
        default=lambda self: self.env['res.lang'].search(
            [('code', '=', self.env.context.get('lang') or 'en_US')],
            limit=1
        )
    )
    parent_id = fields.Many2one(
        'ir.ui.view',
        string='Source View',
        ondelete='cascade',
        index=True,
        required=True
    )
    state = fields.Selection([
        ('draft', 'Draft'),
        ('translated', 'Translated'),
        ('review', 'In Review'), # Kalite kontrol veya onay için
        ('approved', 'Approved'),
        ('needs_work', 'Needs Work') # Geri bildirim sonrası düzeltme için
    ], string='Status', default='draft', tracking=True, index=True, copy=False)
    source = fields.Char("Source", index=True)
    value = fields.Char("Value", index=True)
    parent_id = fields.Many2one('ir.ui.view', string='Parent View')
    quality_score = fields.Integer(
        string="Quality Score",
        compute='_compute_quality_score',
        store=True
    )
    quality_checks = fields.One2many(
        'translation.quality.check',
        'line_id',
        string="Quality Checks"
    )
    last_value = fields.Char("Son Değer")
    sequence = fields.Integer(string="Sequence", default=10)
    key = fields.Char("Key", index=True)
    xml_id = fields.Char("External ID", index=True)
    view_type = fields.Char("View Type")
    max_quality_score = fields.Integer(default=100, store=False, string="Max Quality Score", readonly=True)
    notes = fields.Text(string="Internal Notes")
    xml_id_source = fields.Char(string="XML ID (Source View)", readonly=True, copy=False)
    original_source_id = fields.Many2one('ir.translation', string="Original Source Term (if any)", readonly=True, copy=False)

    # 2. Veritabanı Performans İyileştirmeleri
    _sql_constraints = [
        ('unique_translation_entry',
         'unique(parent_id, lang, source)',
         'This translation already exists!')
    ]

    def action_open_quality_checks(self):
        self.ensure_one()
        return {
            'name': _('Quality Checks for: %s') % (self.name or self.source or 'Line'),
            'type': 'ir.actions.act_window',
            'res_model': 'translation.quality.check',
            'view_mode': 'tree,form',
            'domain': [('line_id', '=', self.id)],
            'context': {'default_line_id': self.id, 'create': True}, # Yeni kayıt oluşturmaya izin ver
            'target': 'new', # Yeni bir pencerede aç
        }
    def run_all_quality_checks_for_line(self):
        self.ensure_one()
        _logger.info(f"Running all quality checks for line ID: {self.id}")
        # TODO: Bu satır için tanımlı tüm kalite kontrollerini tetikleyecek mantığı ekleyin.
        # Örnek: self.quality_checks.run_check() gibi bir şey olabilir veya
        # yeni kontrol kayıtları oluşturup bunları çalıştırabilirsiniz.
        # Sonrasında belki state'i 'review'e alabilirsiniz.
        # if self.state == 'translated':
        #    self.state = 'review'
        return True
    def action_submit_for_review(self):
        self.write({'state': 'review'})

    def action_approve_translation(self):
        self.write({'state': 'approved'})

    def action_mark_as_needs_work(self):
        self.write({'state': 'needs_work'})

    def action_reset_to_draft(self):
        self.write({'state': 'draft'})

    def save_text(self):
        """Çeviriyi Odoo'nun native çeviri sistemine kaydet"""
        self.ensure_one()

        if not self.value:
            raise UserError(_("Translation value cannot be empty!"))

        # View'ın arch_db alanına çeviriyi kaydet
        try:
            # Çeviri verisini hazırla
            translation_data = {
                self.lang.code: {
                    self.source: self.value
                }
            }

            # View'ı güncelle
            view = self.env['ir.ui.view'].sudo().browse(self.parent_id.id)

            # Odoo'nun native update_field_translations metodunu kullan
            view.update_field_translations('arch_db', translation_data)

            # Durumu güncelle
            self.write({
                'state': 'translated',
                'last_value': self.value
            })

            # Başarı mesajı
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Success'),
                    'message': _('Translation saved successfully'),
                    'type': 'success',
                    'sticky': False,
                }
            }

        except Exception as e:
            _logger.error(f"Failed to save translation: {str(e)}")
            raise UserError(_("Failed to save translation: %s") % str(e))

    @api.model
    def action_translate_selected(self):
        """Seçili kayıtları toplu çevir - Server Action için"""
        active_ids = self.env.context.get('active_ids', [])
        if not active_ids:
            raise UserError(_("No records selected!"))

        records = self.browse(active_ids)
        return records.batch_translate()

    def batch_translate(self):
        """Seçili kayıtları toplu olarak çevir"""
        # Sadece çevrilmemiş kayıtları filtrele
        records_to_translate = self.filtered(lambda r: r.source and not r.value)

        if not records_to_translate:
            raise UserError(_("No untranslated records found in selection!"))

        total = len(records_to_translate)
        success = 0
        failed = 0
        errors = []

        # Progress bar için context
        with_context = self.with_context(
            active_test=False,
            prefetch_fields=False,
        )

        for index, record in enumerate(records_to_translate, 1):
            try:
                # Her kayıt için çeviri yap
                record.with_context(**with_context.env.context).translate_text()
                success += 1

                # Her 10 kayıtta bir commit at (performans için)
                if index % 10 == 0:
                    self.env.cr.commit()
                    _logger.info(f"Batch translation progress: {index}/{total}")

            except Exception as e:
                failed += 1
                error_msg = f"Line {record.id} ({record.source[:50]}...): {str(e)}"
                errors.append(error_msg)
                _logger.error(error_msg)
                continue

        # Son commit
        self.env.cr.commit()

        # Sonuç mesajı
        message = _(
            "Translation completed!\n"
            "Total: %(total)d\n"
            "Success: %(success)d\n"
            "Failed: %(failed)d"
        ) % {
            'total': total,
            'success': success,
            'failed': failed
        }

        if errors:
            message += _("\n\nErrors:\n") + "\n".join(errors[:5])  # İlk 5 hata
            if len(errors) > 5:
                message += f"\n... and {len(errors) - 5} more errors"

        # Bildirim göster
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Batch Translation Result'),
                'message': message,
                'type': 'success' if failed == 0 else 'warning',
                'sticky': True,
            }
        }

    @api.model
    def batch_translate_by_language(self, lang_id=None):
        """Belirli bir dil için tüm çevrilmemiş kayıtları çevir"""
        domain = [
            ('source', '!=', False),
            ('value', '=', False)
        ]

        if lang_id:
            domain.append(('lang', '=', lang_id))

        records = self.search(domain)
        return records.batch_translate()

    def batch_translate_with_progress(self):
        """Progress bar ile toplu çeviri (Wizard kullanımı için)"""
        self.ensure_one()

        # Wizard açmak için action döndür
        return {
            'name': _('Batch Translation Progress'),
            'type': 'ir.actions.act_window',
            'res_model': 'translation.batch.wizard',
            'view_mode': 'form',
            'view_id': False,
            'target': 'new',
            'context': {
                'default_line_ids': [(6, 0, self.ids)],
                'default_total_lines': len(self),
            }
        }

    @api.depends('quality_checks.status', 'quality_checks.check_type')
    def _compute_quality_score(self):
        for record in self:
            checks = record.quality_checks
            if not checks:
                record.quality_score = 100
                continue

            score = 100
            for check in checks:
                if check.status == 'error':
                    score -= 20
                elif check.status == 'warning':
                    score -= 10
            record.quality_score = max(0, score)

    # 3. Gelişmiş Hata Yönetimi



    def translate_text(self):
        """DeepL API ile çeviri yapar (Yeniden Denemeli)"""
        self.ensure_one()

        max_retries = 3
        base_delay = 4  # Minimum bekleme süresi (saniye)

        for attempt in range(max_retries):
            try:
                # Cache kontrolü
                source_lang = self.parent_id.get_source_lang()
                # DeepL için özel dil kodu dönüşümü
                target_lang_code = self.lang.code.split('_')[0].upper()

                # Özel dil kodları için mapping
                target_lang_map = {
                    'EN': 'EN-US',  # veya 'EN-GB' - DeepL için spesifik olmalı
                    'PT': 'PT-PT',  # veya 'PT-BR'
                    'ZH': 'ZH'      # Simplified Chinese
                }

                # Eğer mapping'de varsa kullan, yoksa standart kodu kullan
                target_lang = target_lang_map.get(target_lang_code, target_lang_code)

                cached = self.env['translation.cache'].get_cached_translation(
                    self.source,
                    source_lang,
                    target_lang
                )

                if cached:
                    return self.write({'value': cached, 'state': 'translated'})

                # API konfigürasyonu
                config = self.env['ir.config_parameter'].sudo()
                api_key = config.get_param('deepl_translate.deepl_api_key')
                url = config.get_param('deepl_translate.deepl_api_url') or \
                    'https://api-free.deepl.com/v2/translate'

                if not api_key:
                    raise UserError(_("DeepL API key is missing in settings!"))

                # Boş veya çok kısa metinleri kontrol et
                if not self.source or len(self.source.strip()) < 1:
                    _logger.warning(f"Source text is empty or too short: '{self.source}'")
                    return False

                # HTML içerik kontrolü
                is_html = bool(re.search(r'<[^>]+>', self.source))

                # Payload hazırla - None değerleri kaldır
                payload = {
                    'text': [self.source.strip()],
                    'target_lang': target_lang,
                    'source_lang': source_lang,
                }

                # HTML varsa ekle
                if is_html:
                    payload['tag_handling'] = 'html'
                    payload['preserve_formatting'] = '1'

                headers = {
                    'Content-Type': 'application/json',
                    'Authorization': f'DeepL-Auth-Key {api_key}',
                    'User-Agent': 'Odoo-Translation/1.0'
                }

                # Debug için log
                _logger.info(f"DeepL Request - Source: {source_lang}, Target: {target_lang}")
                _logger.debug(f"Payload: {payload}")

                # API çağrısı
                response = requests.post(
                    url,
                    headers=headers,
                    json=payload,
                    timeout=DEEPL_API_TIMEOUT
                )

                # Hata durumunda response içeriğini logla
                if response.status_code != 200:
                    _logger.error(f"DeepL API Error {response.status_code}: {response.text}")

                response.raise_for_status()

                result = response.json()
                translation = result['translations'][0]['text']

                # Veri bütünlüğü kontrolü
                self.validate_translation(translation)

                self.write({
                    'value': translation,
                    'state': 'translated'
                })

                # Cache'e kaydet
                self.env['translation.cache'].set_cache_translation(
                    self.source,
                    source_lang,
                    target_lang,
                    translation
                )

                # Başarılı olduğunda döngüyü kır
                return True

            except requests.exceptions.HTTPError as e:
                if e.response.status_code == 400:
                    # Bad Request - muhtemelen desteklenmeyen dil kombinasyonu
                    error_detail = e.response.text
                    _logger.error(f"DeepL Bad Request: {error_detail}")

                    # Dil kombinasyonu kontrolü
                    if "target_lang" in error_detail or "source_lang" in error_detail:
                        raise UserError(_(
                            "Unsupported language combination.\n"
                            "Source: %(source)s, Target: %(target)s\n"
                            "Please check DeepL documentation for supported languages."
                        ) % {'source': source_lang, 'target': target_lang})
                    else:
                        raise UserError(_(
                            "DeepL API error: %(error)s"
                        ) % {'error': error_detail})

                elif e.response.status_code == 403:
                    raise UserError(_("Invalid DeepL API key. Please check your settings."))

                elif e.response.status_code == 456:
                    raise UserError(_("DeepL quota exceeded. Please check your account."))

                else:
                    # Diğer HTTP hataları için retry
                    if attempt == max_retries - 1:
                        raise UserError(_(
                            "Translation failed after %s attempts. HTTP Error: %s"
                        ) % (max_retries, str(e)))

                    delay = base_delay * (2 ** attempt)
                    _logger.info(f"HTTP error {e.response.status_code}, retrying in {delay} seconds...")
                    time.sleep(delay)

            except (requests.exceptions.RequestException, json.JSONDecodeError) as e:
                _logger.warning(f"Attempt {attempt+1}/{max_retries} failed. Error: {str(e)}")

                if attempt == max_retries - 1:  # Son deneme
                    error_msg = "Translation failed after %s attempts. Final error: %s" % (max_retries, str(e))
                    _logger.error(error_msg)
                    raise UserError(_(error_msg))

                # Üstel bekleyiş hesapla (4, 8, 16 saniye)
                delay = base_delay * (2 ** attempt)
                _logger.info("Retrying in %s seconds...", delay)
                time.sleep(delay)

            except ValidationError as ve:
                # Doğrulama hataları için anında çık
                _logger.error("Validation error: %s", str(ve))
                raise UserError(_("Translation validation failed: %s") % str(ve))

    def validate_translation(self, translation):
        """Çeviri kalite kontrolü"""
        checks = {
            'length': len(translation) > len(self.source) * 3,
            'html_tags': self.compare_html_tags(translation),
            'placeholders': self.compare_placeholders(translation)
        }

        errors = []
        if checks['length']:
            errors.append(_("Translation is too long"))
        if checks['html_tags']:
            errors.append(_("HTML tag mismatch"))
        if checks['placeholders']:
            errors.append(_("Placeholder mismatch"))

        if errors:
            raise ValidationError("\n".join(errors))

    def compare_html_tags(self, translation):
        """HTML etiketlerini karşılaştır"""
        src_tags = re.findall(r'<[^>]+>', self.source)
        tr_tags = re.findall(r'<[^>]+>', translation)
        return set(src_tags) != set(tr_tags)

    def compare_placeholders(self, translation):
        """Yer tutucuları karşılaştır"""
        patterns = [
            r'%(\w+)?s',  # %s, %d vs.
            r'\{[\w]+\}',  # {field}
            r'\{\{.+?\}\}',  # Jinja template variables
            r'\$[A-Z_]+'  # $PLACEHOLDER
        ]

        for pattern in patterns:
            src_ph = set(re.findall(pattern, self.source))
            tr_ph = set(re.findall(pattern, translation))
            if src_ph != tr_ph:
                return True
        return False

    # @queue_job
    def action_translate_selected(self):
        """Toplu çeviri için asenkron iş"""
        records = self.filtered(lambda r: r.source and not r.value)
        for record in records:
            record.with_delay().translate_text()
        return True

