# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
import logging
_logger = logging.getLogger(__name__)

class IrUIView(models.Model):
    _inherit = 'ir.ui.view'

    translation_profile_lines_ids = fields.One2many(
        'translation.profile.lines',
        'parent_id',
        string='Translation Profile Lines',
        auto_join=True  # Performans için
    )

    translation_quality = fields.Float(
        string="Translation Quality",
        compute='_compute_translation_quality',
        store=True
    )

    def get_all_translations(self):
        """View'daki tüm çevrilebilir metinleri toplar - Referans modül mantığı"""
        result = self.get_field_translations('arch_db')

        lines = []
        for item in result[0]:
            text_status = False
            lang_code = item.get("lang")

            if lang_code:
                # Dil kaydını bul (Many2one alan için)
                lang = self.env['res.lang'].search([('code', '=', lang_code)], limit=1)
                if not lang:
                    continue

                # Mevcut kaydı kontrol et
                text_status = self.env['translation.profile.lines'].search([
                    "&", "&",
                    ["lang", "=", lang.id],  # Many2one için ID kullan
                    ["parent_id", "=", self.id],
                    ["source", "=", item.get("source", "")]
                ], limit=1)

                if len(text_status) == 0:
                    # Yeni kayıt oluştur
                    lines.append((0, 0, {
                        'parent_id': self.id,
                        'name': self.name,
                        'key': self.key,
                        'xml_id': self.xml_id,
                        'view_type': str(self.type),
                        'lang': lang.id,  # Many2one için ID
                        'source': item.get("source", ""),
                        'value': item.get("value", ""),
                        'state': 'translated' if item.get("value", "") else 'draft',
                        'sequence': len(lines) + 10,
                    }))

                if len(text_status) == 1:
                    # Mevcut kaydı güncelle
                    text_status.write({
                        'value': item.get("value", ""),
                        'state': 'translated' if item.get("value", "") else 'draft',
                    })

        # Yeni satırları ekle
        self.translation_profile_lines_ids = lines

        return True

    def translate_all(self):
        """View'daki tüm çevrilmemiş satırları çevirir"""
        self.ensure_one()

        untranslated = self.translation_profile_lines_ids.filtered(
            lambda l: l.source and not l.value
        )

        if not untranslated:
            raise UserError(_("No untranslated lines found!"))

        # Progress bilgisi için
        total = len(untranslated)
        translated = 0

        for line in untranslated:
            try:
                line.translate_text()
                translated += 1
                # Her 10 çeviride commit at
                if translated % 10 == 0:
                    self.env.cr.commit()
            except Exception as e:
                _logger.error(f"Translation failed for line {line.id}: {str(e)}")
                continue

        # Başarı mesajı
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Translation Complete'),
                'message': _('%(translated)d of %(total)d lines translated successfully') % {
                    'translated': translated,
                    'total': total
                },
                'type': 'success',
                'sticky': False,
            }
        }

    @api.depends('translation_profile_lines_ids.quality_score')
    def _compute_translation_quality(self):
        """Ortalama çeviri kalitesini hesaplar"""
        for view in self:
            if view.translation_profile_lines_ids:
                scores = [
                    line.quality_score
                    for line in view.translation_profile_lines_ids
                    if line.quality_score is not None
                ]
                view.translation_quality = sum(scores) / len(scores) if scores else 0
            else:
                view.translation_quality = 100

    # 2. Toplu Çeviri İşlemleri
    # def batch_translate_view(self):
    #     """View için toplu çeviri başlat"""
    #     self.ensure_one()
    #     return self.text_lines.action_translate_selected()

    # 3. İçerik Senkronizasyonu
    def sync_translations(self):
        """Odoo'nun yerel çevirileri ile senkronize et"""
        for view in self:
            # Mevcut çevirileri al
            existing_map = {}
            for line in view.translation_profile_lines_ids:
                key = f"{line.lang.code}_{line.source}"
                existing_map[key] = line

            # Odoo çevirilerini al
            translations = self.env['ir.translation'].search([
                ('name', '=', f'ir.ui.view,arch_db'),
                ('res_id', '=', view.id),
                ('type', '=', 'model')
            ])

            new_lines = []
            for trans in translations:
                if not trans.src or not trans.lang:
                    continue

                key = f"{trans.lang}_{trans.src}"
                lang = self.env['res.lang'].search([('code', '=', trans.lang)], limit=1)

                if not lang:
                    continue

                if key in existing_map:
                    # Güncelle
                    if existing_map[key].value != trans.value:
                        existing_map[key].value = trans.value
                else:
                    # Yeni ekle
                    new_lines.append((0, 0, {
                        'parent_id': view.id,
                        'name': f"{view.name} - {trans.lang}",
                        'lang': lang.id,
                        'source': trans.src,
                        'value': trans.value,
                        'state': 'translated' if trans.value else 'draft'
                    }))

            if new_lines:
                view.write({'translation_profile_lines_ids': new_lines})

        return True

    def get_view_translations(self):
        """Odoo'nun yerel çeviri sisteminden çevirileri al"""
        self.ensure_one()
        return self.env['ir.translation'].search_read([
            ('res_id', '=', self.id),
            ('type', '=', 'view')
        ], ['src', 'lang', 'value'])

    def get_source_lang(self):
        """View'ın kaynak dilini döndürür - DeepL formatında"""
        self.ensure_one()

        # Öncelik sırası: context > user > company > system default
        lang_code = (
            self.env.context.get('lang') or
            self.env.user.lang or
            self.env.company.partner_id.lang or
            'en_US'
        )

        # DeepL dil kodu mapping'i
        deepl_lang_map = {
            'en_US': 'EN',
            'en_GB': 'EN',
            'tr_TR': 'TR',
            'de_DE': 'DE',
            'fr_FR': 'FR',
            'es_ES': 'ES',
            'it_IT': 'IT',
            'pt_PT': 'PT-PT',
            'pt_BR': 'PT-BR',
            'nl_NL': 'NL',
            'pl_PL': 'PL',
            'ru_RU': 'RU',
            'ja_JP': 'JA',
            'zh_CN': 'ZH',
            'ko_KR': 'KO',
            'ar_SA': 'AR',
            'bg_BG': 'BG',
            'cs_CZ': 'CS',
            'da_DK': 'DA',
            'el_GR': 'EL',
            'et_EE': 'ET',
            'fi_FI': 'FI',
            'hu_HU': 'HU',
            'id_ID': 'ID',
            'lt_LT': 'LT',
            'lv_LV': 'LV',
            'nb_NO': 'NB',
            'ro_RO': 'RO',
            'sk_SK': 'SK',
            'sl_SI': 'SL',
            'sv_SE': 'SV',
            'uk_UA': 'UK',
        }

        # Mapping'de varsa kullan
        if lang_code in deepl_lang_map:
            return deepl_lang_map[lang_code]

        # Yoksa ilk 2 karakteri al ve büyük harf yap
        base_lang = lang_code.split('_')[0].upper()

        # Varsayılan olarak EN dön
        return base_lang if base_lang else 'EN'

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
