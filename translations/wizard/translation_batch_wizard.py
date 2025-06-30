from odoo import api, fields, models, _
from odoo.exceptions import UserError
import threading
import logging

_logger = logging.getLogger(__name__)


class TranslationBatchWizard(models.TransientModel):
    _name = 'translation.batch.wizard'
    _description = 'Batch Translation Wizard'

    line_ids = fields.Many2many(
        'translation.profile.lines',
        string='Lines to Translate'
    )
    total_lines = fields.Integer(
        string='Total Lines',
        readonly=True
    )
    translated_lines = fields.Integer(
        string='Translated Lines',
        readonly=True,
        default=0
    )
    failed_lines = fields.Integer(
        string='Failed Lines',
        readonly=True,
        default=0
    )
    progress = fields.Float(
        string='Progress',
        compute='_compute_progress',
        readonly=True
    )
    state = fields.Selection([
        ('draft', 'Ready'),
        ('running', 'Running'),
        ('done', 'Completed')
    ], default='draft', string='Status')

    log_text = fields.Text(
        string='Translation Log',
        readonly=True
    )

    # Çeviri ayarları
    skip_cache = fields.Boolean(
        string='Skip Cache',
        help='Skip translation cache and always use API'
    )
    delay_between = fields.Float(
        string='Delay Between Calls (seconds)',
        default=0.5,
        help='Delay between API calls to avoid rate limiting'
    )

    @api.depends('total_lines', 'translated_lines', 'failed_lines')
    def _compute_progress(self):
        for wizard in self:
            if wizard.total_lines > 0:
                completed = wizard.translated_lines + wizard.failed_lines
                wizard.progress = (completed / wizard.total_lines) * 100
            else:
                wizard.progress = 0

    def action_start_translation(self):
        """Toplu çeviriyi başlat"""
        self.ensure_one()

        if self.state != 'draft':
            raise UserError(_("Translation already started!"))

        # Sadece çevrilmemiş kayıtları al
        lines_to_translate = self.line_ids.filtered(
            lambda l: l.source and not l.value
        )

        if not lines_to_translate:
            raise UserError(_("No untranslated lines found!"))

        self.write({
            'state': 'running',
            'total_lines': len(lines_to_translate),
            'log_text': f"Starting translation of {len(lines_to_translate)} lines...\n"
        })

        # Çeviri işlemini başlat
        self._process_translations(lines_to_translate)

        return {
            'type': 'ir.actions.act_window',
            'res_model': self._name,
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'new',
            'context': self.env.context
        }

    def _process_translations(self, lines):
        """Çeviri işlemini gerçekleştir"""
        import time

        translated = 0
        failed = 0
        log_entries = []

        for index, line in enumerate(lines, 1):
            try:
                # Progress güncelle
                self.write({
                    'translated_lines': translated,
                    'failed_lines': failed,
                })

                # Çeviri yap
                if self.skip_cache:
                    line = line.with_context(skip_translation_cache=True)

                line.translate_text()
                translated += 1

                log_entry = f"✓ Line {index}/{len(lines)}: {line.source[:50]}..."
                log_entries.append(log_entry)

                # Delay ekle (rate limiting için)
                if self.delay_between > 0:
                    time.sleep(self.delay_between)

                # Her 5 kayıtta log güncelle
                if index % 5 == 0:
                    self._update_log(log_entries)
                    log_entries = []
                    self.env.cr.commit()

            except Exception as e:
                failed += 1
                log_entry = f"✗ Line {index}/{len(lines)}: Error - {str(e)}"
                log_entries.append(log_entry)
                _logger.error(f"Translation failed for line {line.id}: {str(e)}")
                continue

        # Son güncellemeler
        if log_entries:
            self._update_log(log_entries)

        self.write({
            'state': 'done',
            'translated_lines': translated,
            'failed_lines': failed,
        })

        # Final log
        summary = (
            f"\n{'=' * 50}\n"
            f"Translation completed!\n"
            f"Total: {len(lines)}\n"
            f"Success: {translated}\n"
            f"Failed: {failed}\n"
            f"{'=' * 50}"
        )
        self._update_log([summary])

        return True

    def _update_log(self, entries):
        """Log metnini güncelle"""
        current_log = self.log_text or ""
        new_log = current_log + "\n".join(entries) + "\n"
        self.write({'log_text': new_log})

    def action_close(self):
        """Wizard'ı kapat"""
        return {'type': 'ir.actions.act_window_close'}
