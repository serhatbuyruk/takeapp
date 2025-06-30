# -*- coding: utf-8 -*-

from odoo import models, fields
    
class resCompanyInherit(models.Model):
    _inherit = 'res.company'

    seo_audit_tool_rapid_api_usage_counter = fields.Integer(string="Seo Audit Tool API Usage Counter")
    seo_audit_tool_rapid_api_credit_number = fields.Integer(string="Seo Audit Tool API Credit Number")
    seo_audit_tool_rapid_api_key = fields.Char(string="Seo Audit Tool API RAK")
    seo_audit_tool_rapid_api_host = fields.Char(string="Seo Audit Tool API HOST")

    seo_api_usage_counter = fields.Integer(string="Seo API Usage Counter")
    seo_api_credit_number = fields.Integer(string="Seo API Credit Number")
    seo_api_key = fields.Char(string="Seo API RAK")
    seo_api_host = fields.Char(string="Seo API HOST")

    seo_checker_api_usage_counter = fields.Integer(string="Seo Checker Usage Counter")
    seo_checker_api_credit_number = fields.Integer(string="Seo Checker Credit Number")
    seo_checker_api_key = fields.Char(string="Seo Checker RAK")
    seo_checker_api_host = fields.Char(string="Seo Checker HOST")

    seo_fast_extraction_usage_counter = fields.Integer(string="Seo Fast Extraction Usage Counter")
    seo_fast_extraction_credit_number = fields.Integer(string="Seo Fast Extraction Credit Number")
    seo_fast_extraction_key = fields.Char(string="Seo Fast Extraction RAK")
    seo_fast_extraction_host = fields.Char(string="Seo Fast Extraction HOST")

    keyword_autosuggest_usage_counter = fields.Integer(string="Keyword Autosuggest Usage Counter")
    keyword_autosuggest_credit_number = fields.Integer(string="Keyword Autosuggest Credit Number")
    keyword_autosuggest_key = fields.Char(string="Keyword Autosuggest RAK")
    keyword_autosuggest_host = fields.Char(string="Keyword Autosuggest HOST")

    da_pa_and_spam_usage_counter = fields.Integer(string="DA/PA and Spam Usage Counter")
    da_pa_and_spam_credit_number = fields.Integer(string="DA/PA and Spam Credit Number")
    da_pa_and_spam_key = fields.Char(string="DA/PA and Spam RAK")
    da_pa_and_spam_host = fields.Char(string="DA/PA and Spam HOST")

    seox_usage_counter = fields.Integer(string="Seox Usage Counter")
    seox_credit_number = fields.Integer(string="Seox Credit Number")
    seox_key = fields.Char(string="Seox RAK")
    seox_host = fields.Char(string="Seox HOST")

    google_seo_keyword_research_usage_counter = fields.Integer(string="Google Seo Keyword Research Usage Counter")
    google_seo_keyword_research_credit_number = fields.Integer(string="Google Seo Keyword Research Credit Number")
    google_seo_keyword_research_key = fields.Char(string="Google Seo Keyword Research RAK")
    google_seo_keyword_research_host = fields.Char(string="Google Seo Keyword Research HOST")

    keyword_suggestion_api_usage_counter = fields.Integer(string="Keyword Suggestion Api Usage Counter")
    keyword_suggestion_api_credit_number = fields.Integer(string="Keyword Suggestion Api Credit Number")
    keyword_suggestion_api_key = fields.Char(string="Keyword Suggestion Api RAK")
    keyword_suggestion_api_host = fields.Char(string="Keyword Suggestion Api HOST")

    google_api_usage_counter = fields.Integer(string="Google Api Usage Counter")
    google_api_credit_number = fields.Integer(string="Google Api Credit Number")
    google_api_key = fields.Char(string="Google Api RAK")
    google_api_host = fields.Char(string="Google Api HOST")

    scraper_tech_usage_counter = fields.Integer(string="Scraper-Tech Api Usage Counter")
    scraper_tech_credit_number = fields.Integer(string="Scraper-Tech Credit Number")
    scraper_tech_key = fields.Char(string="Scraper-Tech RAK")
    scraper_tech_host = fields.Char(string="Scraper-Tech HOST")

    regim_usage_counter = fields.Integer(string="Regim Api Usage Counter")
    regim_credit_number = fields.Integer(string="Regim Credit Number")
    regim_key = fields.Char(string="Regim RAK")
    regim_host = fields.Char(string="Regim HOST")
    
    
