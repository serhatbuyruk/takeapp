# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
import logging
_logger = logging.getLogger(__name__)

class TranslationQualityCheck(models.Model):
    _name = 'translation.quality.check'
    _description = 'Translation Quality Assurance'

    line_id = fields.Many2one(
        'translation.profile.lines',
        string="Translation Line",
        required=True,
        ondelete='cascade'
    )
    check_type = fields.Selection([
        ('length', 'Length Check'),
        ('tags', 'HTML Tags'),
        ('placeholders', 'Placeholders'),
        ('consistency', 'Consistency')
    ], string="Check Type", required=True)
    status = fields.Selection([
        ('pass', 'Passed'),
        ('warning', 'Warning'),
        ('error', 'Error'),
        ('pending', 'Pending')
    ], string="Status", default='pending', required=True)
    details = fields.Text("Detailed Report")

    # 1. Otomatik Düzeltme
    def auto_correct_issues(self):
        """Seçili sorunları otomatik düzelt"""
        for check in self.filtered('auto_correctible'):
            if check.check_type == 'tags':
                check.correct_html_tags()
            elif check.check_type == 'placeholders':
                check.correct_placeholders()

    # 2. Gelişmiş HTML Düzeltme
    def correct_html_tags(self):
        """Eksik HTML tag'lerini ekle"""
        missing = set(re.findall(r'<[^>]+>', self.line_id.source)) - \
                  set(re.findall(r'<[^>]+>', self.line_id.value))

        if missing:
            corrected = self.line_id.value + ' ' + ' '.join(missing)
            self.line_id.write({'value': corrected})

    # 3. Gelişmiş Raporlama
    def generate_quality_report(self):
        """PDF formatında kalite raporu oluştur"""
        report = self.env['ir.actions.report'].search(
            [('report_name', '=', 'translation_quality_report')],
            limit=1
        )
        return report.report_action(self)

    def run_check(self):
        self.ensure_one()
        _logger.info(f"Running quality check ID: {self.id}, Type: {self.check_type} for Line ID: {self.line_id.id}")

        # Bu spesifik kontrolü (self.check_type) yeniden çalıştıracak mantığı buraya ekleyin.
        # Örneğin:
        new_status = 'pending'
        new_details = "Check re-initiated."

        if self.check_type == 'length':
            # Uzunluk kontrolü mantığı
            # source_len = len(self.line_id.source or '')
            # value_len = len(self.line_id.value or '')
            # if value_len > source_len * 3 and source_len > 0 : # Basit bir örnek
            #     new_status = 'error'
            #     new_details = f"Translated text ({value_len} chars) is much longer than source ({source_len} chars)."
            # elif value_len == 0 and source_len > 0:
            #     new_status = 'warning'
            #     new_details = "Translation is empty."
            # else:
            #     new_status = 'pass'
            #     new_details = "Length check passed."
            pass # Gerçek kontrol mantığını ekleyin
        elif self.check_type == 'tags':
            # HTML etiket kontrolü mantığı
            # if self.line_id.compare_html_tags(self.line_id.value or ''): # compare_html_tags metodu line_id'de olmalı
            #    new_status = 'error'
            #    new_details = "HTML tag mismatch detected."
            # else:
            #    new_status = 'pass'
            #    new_details = "HTML tags match."
            pass # Gerçek kontrol mantığını ekleyin
        elif self.check_type == 'placeholders':
            # Yer tutucu kontrolü mantığı
            pass # Gerçek kontrol mantığını ekleyin
        elif self.check_type == 'consistency':
            # Tutarlılık kontrolü mantığı
            pass # Gerçek kontrol mantığını ekleyin
        else:
            new_details = f"No specific logic defined for re-running check type: {self.check_type}"
            # new_status 'pending' olarak kalabilir veya bir hata durumu olabilir

        self.write({
            'status': new_status,
            'details': new_details
        })
        # İsteğe bağlı: Bu kontrol çalıştıktan sonra line_id'nin quality_score'unu yeniden hesaplatabilirsiniz.
        # self.line_id._compute_quality_score() # Bu direkt çağrı yerine field'ı recompute etmek daha iyi olabilir
        # self.line_id.invalidate_recordset(['quality_score']) # Veya ORM cache'ini geçersiz kılın
        return True
