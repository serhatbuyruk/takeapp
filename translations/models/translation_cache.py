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

class TranslationCache(models.Model):
    _name = 'translation.cache'
    _description = 'Translation Cache'
    _order = 'hit_count DESC, create_date DESC'
    _rec_name = 'source_text'

    source_text = fields.Char(
        string="Source Text",
        required=True,
        index=True
    )
    translated_text = fields.Text(
        string="Translated Text",
        required=True
    )
    source_lang = fields.Char(
        string="Source Language",
        required=True,
        index=True
    )
    target_lang = fields.Char(
        string="Target Language",
        required=True,
        index=True
    )
    provider = fields.Char(
        string="Translation Provider",
        default="deepl"
    )
    create_date = fields.Datetime(
        string="Create Date",
        default=fields.Datetime.now,
        index=True
    )
    hit_count = fields.Integer(
        string="Hit Count",
        default=1
    )
    quality_check = fields.Boolean(
        string="Quality Checked",
        default=False
    )

    _sql_constraints = [
        ('unique_translation',
         'unique(source_text, source_lang, target_lang)',
         'This translation already exists in cache!')
    ]

    @api.model
    def get_cached_translation(self, source, source_lang, target_lang):
        """Cache'den çeviri getir"""
        cache = self.search([
            ('source_text', '=', source),
            ('source_lang', '=', source_lang),
            ('target_lang', '=', target_lang)
        ], limit=1)

        if cache:
            # Hit count'u artır
            cache.sudo().write({'hit_count': cache.hit_count + 1})
            return cache.translated_text
        return None

    @api.model
    def set_cache_translation(self, source, source_lang, target_lang, translation, provider="deepl"):
        """Cache'e çeviri ekle veya güncelle"""
        existing = self.search([
            ('source_text', '=', source),
            ('source_lang', '=', source_lang),
            ('target_lang', '=', target_lang)
        ], limit=1)

        if existing:
            existing.sudo().write({
                'translated_text': translation,
                'hit_count': existing.hit_count + 1,
                'provider': provider
            })
        else:
            self.sudo().create({
                'source_text': source,
                'source_lang': source_lang,
                'target_lang': target_lang,
                'translated_text': translation,
                'provider': provider,
                'hit_count': 1
            })

        return True

    @api.model
    def clean_old_cache(self, days=30):
        """Eski cache kayıtlarını temizle"""
        cutoff_date = fields.Datetime.now() - timedelta(days=days)
        old_cache = self.search([
            ('create_date', '<', cutoff_date),
            ('hit_count', '<', 3)  # Az kullanılan kayıtları sil
        ])

        count = len(old_cache)
        old_cache.unlink()

        _logger.info(f"Cleaned {count} old cache entries older than {days} days")
        return count

    @api.model
    def preload_cache(self, batch_size=500):
        """Mevcut çevirileri cache'e yükle"""
        # Kullanıcının varsayılan dili
        source_lang_code = self.env.user.lang or 'en_US'
        source_lang = source_lang_code.split('_')[0].upper()

        # Mevcut çevirileri al
        translations = self.env['translation.profile.lines'].search_read(
            [('value', '!=', False)],
            ['source', 'lang', 'value'],
            limit=batch_size
        )

        batch = []
        for trans in translations:
            # Dil kodunu al
            lang_rec = self.env['res.lang'].browse(trans['lang'][0])
            target_lang = lang_rec.code.split('_')[0].upper() if lang_rec else 'EN'

            batch.append({
                'source_text': trans['source'],
                'source_lang': source_lang,
                'target_lang': target_lang,
                'translated_text': trans['value'],
                'provider': 'preload'
            })

            if len(batch) >= 100:  # 100'lük gruplar halinde ekle
                self.create(batch)
                batch = []
                self.env.cr.commit()  # Bellek yönetimi için

        if batch:
            self.create(batch)

        return len(translations)

    def action_mark_quality_checked(self):
        """Seçili cache kayıtlarını kalite kontrollü olarak işaretle"""
        self.write({'quality_check': True})
        return True

    def action_clear_cache(self):
        """Tüm cache'i temizle (dikkatli kullan!)"""
        if self.env.user.has_group('base.group_system'):
            count = self.search_count([])
            self.search([]).unlink()
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Cache Cleared'),
                    'message': _('%d cache entries deleted') % count,
                    'type': 'warning'
                }
            }
        else:
            raise UserError(_("Only system administrators can clear the cache!"))
