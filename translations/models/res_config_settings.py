from odoo import models, fields, api

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    deepl_api_key = fields.Char(string="DeepL API Key", config_parameter='deepl_translate.deepl_api_key')
    deepl_api_url = fields.Char(string="DeepL API URL", config_parameter='deepl_translate.deepl_api_url', default='https://api-free.deepl.com/v2/translate')
