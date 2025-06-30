# -*- coding: utf-8 -*-

from odoo import tools, fields, models, api,_
from odoo.exceptions import UserError
from odoo.exceptions import ValidationError
cookie = "translation"

class translationsProfile(models.Model):
    _name = "translation.profile"
    _description = "Translation Profile" # Açıklama eklemek iyi bir pratiktir
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = "sequence, name" # Sıralama eklendi

    name = fields.Char(string="Name", required=True, tracking=True) # required=True eklendi
    sequence = fields.Integer(string="Sequence", default=10)
    description = fields.Text(string="Description")
    state = fields.Selection([
        ('draft', 'Draft'),
        ('active', 'Active'),
        ('archived', 'Archived')
    ], string="Status", default='draft', tracking=True)
    color = fields.Integer(string='Color Index') # Renk seçici için

    view_ids = fields.Many2many('ir.ui.view', string="Associated Views")

    # Örnek bir compute alanı (Python'da tanımlanmalı)
    line_count = fields.Integer(string="Line Count", compute='_compute_line_count', store=False)

    @api.depends('view_ids.translation_profile_lines_ids')
    def _compute_line_count(self):
        for profile in self:
            count = 0
            if profile.view_ids:
                for view in profile.view_ids:
                    # DÜZELTİLMİŞ ALAN REFERANSI
                    count += len(view.translation_profile_lines_ids)
            profile.line_count = count

    # Görünümlerdeki butonlar için metodlar (Python'da tanımlanmalı)
    def action_import_translations(self):
        # Import逻辑
        return True

    def action_export_translations(self):
        # Export逻辑
        return True

    def create_new_lines(self): # Bu metodun ne yapacağı netleştirilmeli
        # Belki seçili view_ids'den satır oluşturur?
        return True

    def action_translate_all(self): # Bu metodun ne yapacağı netleştirilmeli
        # Belki ilişkili tüm satırları çevirir?
        return True
