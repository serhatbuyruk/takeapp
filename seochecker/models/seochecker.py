import base64
import os
import tempfile
from odoo import tools, fields, models, api,_
import requests
import json, logging
from datetime import datetime
from base64 import b64encode
from odoo.exceptions import UserError
from odoo.exceptions import ValidationError
import uuid

import urllib.request
import urllib.error


from bs4 import BeautifulSoup
from collections import Counter
import nltk

from seoanalyzer import analyze

_logger = logging.getLogger(__name__)


# For DataCounter
############################
# import os
# import docx
# import docx2txt
# import re
# import tempfile
# import base64
# import logging
# import magic
# import pytesseract
# import pdfminer
# from pdfminer.high_level import extract_text # pdfminer.six
# from PIL import Image
############################

cookie = "seochecker"

class seocheckerProfile(models.Model):
    _name = "seochecker.profile"
    _inherit = "mail.thread"
    
    name = fields.Char(string="Name")
    visibility = fields.Boolean(string="Visibility", default=True)
    user_access = fields.Many2many('res.users',relation='x_seochecker_profile_res_users_rel', column1='seochecker_users_id',column2='res_users_id', string="Users Can Edit")
    image_of_website = fields.Binary(string="Image")
    sequence = fields.Integer(string="Sequence")
    priority = fields.Selection([('1','1'),('2','2'),('3','3'),('4','4'),('5','5')],
                                    string="Priority ", default="1", tracking=True
                                    ) 
    color = fields.Integer(string='Color')
    product_id = fields.Many2one('product.product', string="Product", tracking=True)
    sale_id = fields.Many2one('sale.order', string="Sale", tracking=True)
    description = fields.Char(string="Description", tracking=True)
    uuid = fields.Char(string="uuid")
    
    title = fields.Char(string="Title")
    content = fields.Char(string="Content")
    headings = fields.Char(string="Headings")
    number_of_images = fields.Integer(string="Number Of Images")

    seo_text_file = fields.Many2many('ir.attachment','attachment_rel_1','pro_id_1','attach_id_1', string='Text File Attachments',) 
    seo_visual_file = fields.Many2many('ir.attachment','attachment_rel_2','pro_id_2','attach_id_2', string='Visual File Attachments',)
    
    contact_name = fields.Char(string="Contact Name")
    company_name = fields.Char(string="Company Name")
    street = fields.Char(string="Street")
    city = fields.Char(string="City")
    state = fields.Many2one('res.country.state', string="State", domain="[('country_id', '=', country_id)]")
    country_id = fields.Many2one('res.country', string="Country")
    language_id = fields.Many2one('res.lang', string="Languages")
    competitor_websites = fields.Many2many('seochecker.profile',relation='x_seochecker_profile_seochecker_profile_rel', column1='id1',column2='id2', string="Competitor Websites")

    company_id = fields.Many2one('res.partner', string="Company", tracking=True)
    
    user = fields.Many2one('res.users', string="User")
    user_notification = fields.Boolean(string="User Notification", default=True, tracking=True)
    responsible_employee = fields.Many2one('res.partner', string="Responsible Employee", tracking=True)

    website = fields.Char(string="Website")
    main_website = fields.Boolean(string="Main Website", default=False, tracking=True)
    keywords = fields.Char(string="Keywords")
    related_main_website_id = fields.Integer(string="Related Main Website Id")
    related_main_website = fields.Many2one('seochecker.profile', string="Related Main Website")
    
    seo_audit_tool_api_response = fields.Char(string="SEO Audit Tool API Response")
    https_status = fields.Boolean(string="Https Status")
    content_size = fields.Char(string="Content Size (Bytes)")
    response_time = fields.Char(string="Response Time")
    title_data = fields.Char(string="Title Data")
    title_length = fields.Integer(string="Title Length")
    meta_description_data = fields.Char(string="Meta Description Data")
    meta_description_length = fields.Integer(string="Meta Description Length")
    metadata_canonical = fields.Char(string="Meta Canonical")
    meta_favicon = fields.Char(string="Meta Favicon")
    meta_keywords = fields.Char(string="Meta Keywords")
    meta_locale = fields.Char(string="Meta Locale")
    meta_site_name = fields.Char(string="Meta Site Name")
    meta_site_image = fields.Char(string="Meta Site Image")
    page_headings_summary = fields.Char(string="Page Headings Summary")
    word_count_total = fields.Integer(string="Word Count Total")
    anchor_text_words = fields.Integer(string="Anchor Text Words")
    anchor_percentage = fields.Float(string="Anchor Percentage")
    total_links = fields.Integer(string="Total Links")
    links_href = fields.Char(string="Links Href")
    links_text = fields.Char(string="Links Text")
    images_total_number = fields.Integer(string="Images Total Number")
    images_no_src_tag_number = fields.Integer(string="Images No Src Tags Number")
    images_no_alt_tag_number = fields.Integer(string="Images No Alt Tags Number")
    images_data_src = fields.Char(string="Images Data Src")
    images_data_alt = fields.Char(string="Images Data Alt")


    seo_api_page_size_response = fields.Char(string="Page Size Response")
    seo_api_meta_tags_analyzer_response = fields.Char(string="Meta Tags Analyzer Response")
    seo_api_keyword_rank_checker_response = fields.Char(string="Rank Checker Response")
    seo_api_keyword_density_response = fields.Char(string="Keyword Density Response")
    seo_api_detected_keywords = fields.Char(string="Detected Keywords")

    seo_checker_analyzev2_desktop_response = fields.Char(string="Analyze Desktop Response")
    seo_checker_analyzev2_mobile_response = fields.Char(string="Analyze Mobile Response")
    seo_checker_performance_analyzev2_desktop_response = fields.Char(string="Analyze Performance Desktop Response")
    seo_checker_performance_analyzev2_mobile_response = fields.Char(string="Analyze Performance Mobile Response")
    seo_checker_category = fields.Selection([('accessibility','accessibility'),('best-practices','best-practices'),('performance','performance'),('seo','seo'),('pwa','pwa')],
                                    string="Category ", default="seo", tracking=True
                                    )
    seo_checker_strategy = fields.Selection([('desktop','desktop'),('mobile','mobile')],
    string="Strategy ", default="desktop", tracking=True
    )
    seo_checker_seo_score_desktop = fields.Float(string="Seo Score Desktop")
    seo_checker_seo_score_mobile = fields.Float(string="Seo Score Mobile")
    seo_checker_performance_score_desktop = fields.Float(string="Performance Score Desktop")
    seo_checker_performance_score_mobile = fields.Float(string="Performance Score Mobile")
    seo_checker_accessibility_score_desktop = fields.Float(string="Accessibility Score Desktop")
    seo_checker_accessibility_score_mobile = fields.Float(string="Accessibility Score Mobile")
    seo_checker_best_practices_score_desktop = fields.Float(string="Best Practices Score Desktop")
    seo_checker_best_practices_score_mobile = fields.Float(string="Best Practices Score Mobile")
    seo_checker_pwa_score_desktop = fields.Float(string="Pwa Score Desktop")
    seo_checker_pwa_score_mobile = fields.Float(string="Pwa Score Mobile")
    seo_checker_desktop_font_size_title = fields.Char(string="Font-Size Title")
    seo_checker_desktop_font_size_description = fields.Char(string="Font-Size Description")
    seo_checker_desktop_font_size_score = fields.Float(string="Font-Size Score")
    seo_checker_desktop_link_text_title = fields.Char(string="Link-Text Title")
    seo_checker_desktop_link_text_description = fields.Char(string="Link-Text Description")
    seo_checker_desktop_link_text_score = fields.Float(string="Link-Text Score")
    seo_checker_desktop_tap_targets_title = fields.Char(string="Tap-Targets Title")
    seo_checker_desktop_tap_targets_description = fields.Char(string="Tap-Targets Description")
    seo_checker_desktop_tap_targets_score = fields.Float(string="Tap-Targets Score")
    seo_checker_desktop_http_status_code_title = fields.Char(string="Http Status Title")
    seo_checker_desktop_http_status_code_description = fields.Char(string="Http Status Description")
    seo_checker_desktop_http_status_code_score = fields.Float(string="Http Status Score")
    seo_checker_desktop_crawlable_anchors_title = fields.Char(string="Crawlable Anchors Title")
    seo_checker_desktop_crawlable_anchors_description = fields.Char(string="Crawlable Anchors Description")
    seo_checker_desktop_crawlable_anchors_score = fields.Float(string="Crawlable Anchors Score")
    seo_checker_desktop_crawlable_anchors_items = fields.Char(string="Crawlable Anchors Items")
    seo_checker_desktop_is_crawlable_title = fields.Char(string="Is-Crawable Title")
    seo_checker_desktop_is_crawlable_description = fields.Char(string="Is-Crawable Description")
    seo_checker_desktop_is_crawlable_score = fields.Float(string="Is-Crawable Score")
    seo_checker_desktop_meta_description_title = fields.Char(string="Meta-Description Title")
    seo_checker_desktop_meta_description_description = fields.Char(string="Meta-Description Description")
    seo_checker_desktop_meta_description_score = fields.Float(string="Meta-Description Score")
    seo_checker_desktop_structured_data_title = fields.Char(string="Structured Data Title")
    seo_checker_desktop_structured_data_description = fields.Char(string="Structured Data Description")
    seo_checker_desktop_structured_data_score = fields.Float(string="Structured Data Score")
    seo_checker_desktop_robots_txt_title = fields.Char(string="Robots-Txt Title")
    seo_checker_desktop_robots_txt_description = fields.Char(string="Robots-Txt Description")
    seo_checker_desktop_robots_txt_score = fields.Float(string="Robots-Txt Score")
    seo_checker_desktop_document_title_title = fields.Char(string="Document-Title Title")
    seo_checker_desktop_document_title_description = fields.Char(string="Document-Title Description")
    seo_checker_desktop_document_title_score = fields.Float(string="Document-Title Score")
    seo_checker_desktop_document_title_item = fields.Char(string="Document-Title Item")
    seo_checker_desktop_viewport_title = fields.Char(string="Viewport Title")
    seo_checker_desktop_viewport_description = fields.Char(string="Viewport Description")
    seo_checker_desktop_viewport_score = fields.Float(string="Viewport Score")
    seo_checker_desktop_canonical_title = fields.Char(string="Canonical Title")
    seo_checker_desktop_canonical_description = fields.Char(string="Canonical Description")
    seo_checker_desktop_canonical_score = fields.Float(string="Canonical Score")
    seo_checker_desktop_image_alt_title = fields.Char(string="Image-Alt Title")
    seo_checker_desktop_image_alt_description = fields.Char(string="Image-Alt Description")
    seo_checker_desktop_image_alt_score = fields.Float(string="Image-Alt Score")
    seo_checker_desktop_image_alt_item = fields.Char(string="Image Alt Item")
    seo_checker_desktop_plugins_title = fields.Char(string="Plugins Title")
    seo_checker_desktop_plugins_description = fields.Char(string="Plugins Description")
    seo_checker_desktop_plugins_score = fields.Float(string="Plugins Score")
    seo_checker_desktop_hreflang_title = fields.Char(string="Hreflang Title")
    seo_checker_desktop_hreflang_description = fields.Char(string="Hreflang Description")
    seo_checker_desktop_hreflang_score = fields.Float(string="Hreflang Score")
    
    seo_checker_screenshot = fields.Binary(string="Seo Checker Screenshot")

    seo_checker_mobile_font_size_title = fields.Char(string="Font-Size Title")
    seo_checker_mobile_font_size_description = fields.Char(string="Font-Size Description")
    seo_checker_mobile_font_size_score = fields.Float(string="Font-Size Score")
    seo_checker_mobile_link_text_title = fields.Char(string="Link-Text Title")
    seo_checker_mobile_link_text_description = fields.Char(string="Link-Text Description")
    seo_checker_mobile_link_text_score = fields.Float(string="Link-Text Score")
    seo_checker_mobile_tap_targets_title = fields.Char(string="Tap-Targets Title")
    seo_checker_mobile_tap_targets_description = fields.Char(string="Tap-Targets Description")
    seo_checker_mobile_tap_targets_score = fields.Float(string="Tap-Targets Score")
    seo_checker_mobile_http_status_code_title = fields.Char(string="Http Status Title")
    seo_checker_mobile_http_status_code_description = fields.Char(string="Http Status Description")
    seo_checker_mobile_http_status_code_score = fields.Float(string="Http Status Score")
    seo_checker_mobile_crawlable_anchors_title = fields.Char(string="Crawlable Anchors Title")
    seo_checker_mobile_crawlable_anchors_description = fields.Char(string="Crawlable Anchors Description")
    seo_checker_mobile_crawlable_anchors_score = fields.Float(string="Crawlable Anchors Score")
    seo_checker_mobile_crawlable_anchors_items = fields.Char(string="Crawlable Anchors Items")
    seo_checker_mobile_is_crawlable_title = fields.Char(string="Is-Crawable Title")
    seo_checker_mobile_is_crawlable_description = fields.Char(string="Is-Crawable Description")
    seo_checker_mobile_is_crawlable_score = fields.Float(string="Is-Crawable Score")
    seo_checker_mobile_meta_description_title = fields.Char(string="Meta-Description Title")
    seo_checker_mobile_meta_description_description = fields.Char(string="Meta-Description Description")
    seo_checker_mobile_meta_description_score = fields.Float(string="Meta-Description Score")
    seo_checker_mobile_structured_data_title = fields.Char(string="Structured Data Title")
    seo_checker_mobile_structured_data_description = fields.Char(string="Structured Data Description")
    seo_checker_mobile_structured_data_score = fields.Float(string="Structured Data Score")
    seo_checker_mobile_robots_txt_title = fields.Char(string="Robots-Txt Title")
    seo_checker_mobile_robots_txt_description = fields.Char(string="Robots-Txt Description")
    seo_checker_mobile_robots_txt_score = fields.Float(string="Robots-Txt Score")
    seo_checker_mobile_document_title_title = fields.Char(string="Document-Title Title")
    seo_checker_mobile_document_title_description = fields.Char(string="Document-Title Description")
    seo_checker_mobile_document_title_score = fields.Float(string="Document-Title Score")
    seo_checker_mobile_document_title_item = fields.Char(string="Document-Title Item")
    seo_checker_mobile_viewport_title = fields.Char(string="Viewport Title")
    seo_checker_mobile_viewport_description = fields.Char(string="Viewport Description")
    seo_checker_mobile_viewport_score = fields.Float(string="Viewport Score")
    seo_checker_mobile_canonical_title = fields.Char(string="Canonical Title")
    seo_checker_mobile_canonical_description = fields.Char(string="Canonical Description")
    seo_checker_mobile_canonical_score = fields.Float(string="Canonical Score")
    seo_checker_mobile_image_alt_title = fields.Char(string="Image-Alt Title")
    seo_checker_mobile_image_alt_description = fields.Char(string="Image-Alt Description")
    seo_checker_mobile_image_alt_score = fields.Float(string="Image-Alt Score")
    seo_checker_mobile_image_alt_item = fields.Char(string="Image Alt Item")
    seo_checker_mobile_plugins_title = fields.Char(string="Plugins Title")
    seo_checker_mobile_plugins_description = fields.Char(string="Plugins Description")
    seo_checker_mobile_plugins_score = fields.Float(string="Plugins Score")
    seo_checker_mobile_hreflang_title = fields.Char(string="Hreflang Title")
    seo_checker_mobile_hreflang_description = fields.Char(string="Hreflang Description")
    seo_checker_mobile_hreflang_score = fields.Float(string="Hreflang Score")

    seo_checker_desktop_largest_contentful_paint_title = fields.Char(string="largest-contentful-paint Title")
    seo_checker_desktop_largest_contentful_paint_description = fields.Char(string="largest-contentful-paint Description")
    seo_checker_desktop_largest_contentful_paint_score = fields.Float(string="largest-contentful-paint Score")
    seo_checker_desktop_largest_contentful_paint_diplay_value = fields.Char(string="largest-contentful-paint Display Value")
    seo_checker_desktop_largest_contentful_paint_numeric_unit = fields.Char(string="largest-contentful-paint Numeric Unit")
    seo_checker_desktop_total_blocking_time_title = fields.Char(string="total_blocking_time Title")
    seo_checker_desktop_total_blocking_time_description = fields.Char(string="total_blocking_time Description")
    seo_checker_desktop_total_blocking_time_score = fields.Float(string="total_blocking_time Score")
    seo_checker_desktop_total_blocking_time_diplay_value = fields.Char(string="total_blocking_time Display Value")
    seo_checker_desktop_total_blocking_time_numeric_unit = fields.Char(string="total_blocking_time Numeric Unit")
    seo_checker_desktop_cumulative_layout_shift_title = fields.Char(string="cumulative_layout_shift Title")
    seo_checker_desktop_cumulative_layout_shift_description = fields.Char(string="cumulative_layout_shift Description")
    seo_checker_desktop_cumulative_layout_shift_score = fields.Float(string="cumulative_layout_shift Score")
    seo_checker_desktop_cumulative_layout_shift_diplay_value = fields.Char(string="cumulative_layout_shift Display Value")
    seo_checker_desktop_cumulative_layout_shift_numeric_unit = fields.Char(string="cumulative_layout_shift Numeric Unit")
    seo_checker_desktop_speed_index_title = fields.Char(string="speed_index Title")
    seo_checker_desktop_speed_index_description = fields.Char(string="speed_index Description")
    seo_checker_desktop_speed_index_score = fields.Float(string="speed_index Score")
    seo_checker_desktop_speed_index_diplay_value = fields.Char(string="speed_index Display Value")
    seo_checker_desktop_speed_index_numeric_unit = fields.Char(string="speed_index Numeric Unit")
    seo_checker_desktop_interactive_title = fields.Char(string="interactive Title")
    seo_checker_desktop_interactive_description = fields.Char(string="interactive Description")
    seo_checker_desktop_interactive_score = fields.Float(string="interactive Score")
    seo_checker_desktop_interactive_diplay_value = fields.Char(string="interactive Display Value")
    seo_checker_desktop_interactive_numeric_unit = fields.Char(string="interactive Numeric Unit")
    seo_checker_desktop_server_response_time_title = fields.Char(string="server_response_time Title")
    seo_checker_desktop_server_response_time_description = fields.Char(string="server_response_time Description")
    seo_checker_desktop_server_response_time_score = fields.Float(string="server_response_time Score")
    seo_checker_desktop_server_response_time_diplay_value = fields.Char(string="server_response_time Display Value")
    seo_checker_desktop_server_response_time_numeric_unit = fields.Char(string="server_response_time Numeric Unit")
    seo_checker_desktop_total_byte_weight_title = fields.Char(string="total_byte_weight Title")
    seo_checker_desktop_total_byte_weight_description = fields.Char(string="total_byte_weight Description")
    seo_checker_desktop_total_byte_weight_score = fields.Float(string="total_byte_weight Score")
    seo_checker_desktop_total_byte_weight_diplay_value = fields.Char(string="total_byte_weight Display Value")
    seo_checker_desktop_total_byte_weight_numeric_unit = fields.Char(string="total_byte_weight Numeric Unit")
    seo_checker_desktop_render_blocking_resources_title = fields.Char(string="render_blocking_resources Title")
    seo_checker_desktop_render_blocking_resources_description = fields.Char(string="render_blocking_resources Description")
    seo_checker_desktop_render_blocking_resources_score = fields.Float(string="render_blocking_resources Score")
    seo_checker_desktop_render_blocking_resources_diplay_value = fields.Char(string="render_blocking_resources Display Value")
    seo_checker_desktop_render_blocking_resources_numeric_unit = fields.Char(string="render_blocking_resources Numeric Unit")
    seo_checker_desktop_unused_css_rules_title = fields.Char(string="unused_css_rules Title")
    seo_checker_desktop_unused_css_rules_description = fields.Char(string="unused_css_rules Description")
    seo_checker_desktop_unused_css_rules_score = fields.Float(string="unused_css_rules Score")
    seo_checker_desktop_unused_css_rules_diplay_value = fields.Char(string="unused_css_rules Display Value")
    seo_checker_desktop_unused_css_rules_numeric_unit = fields.Char(string="unused_css_rules Numeric Unit")
    seo_checker_desktop_unused_javascript_title = fields.Char(string="unused_javascript Title")
    seo_checker_desktop_unused_javascript_description = fields.Char(string="unused_javascript Description")
    seo_checker_desktop_unused_javascript_score = fields.Float(string="unused_javascript Score")
    seo_checker_desktop_unused_javascript_diplay_value = fields.Char(string="unused_javascript Display Value")
    seo_checker_desktop_unused_javascript_numeric_unit = fields.Char(string="unused_javascript Numeric Unit")
    seo_checker_desktop_duplicated_javascript_title = fields.Char(string="duplicated_javascript Title")
    seo_checker_desktop_duplicated_javascript_description = fields.Char(string="duplicated_javascript Description")
    seo_checker_desktop_duplicated_javascript_score = fields.Float(string="duplicated_javascript Score")
    seo_checker_desktop_duplicated_javascript_diplay_value = fields.Char(string="duplicated_javascript Display Value")
    seo_checker_desktop_duplicated_javascript_numeric_unit = fields.Char(string="duplicated_javascript Numeric Unit")
    seo_checker_desktop_modern_image_formats_title = fields.Char(string="modern_image_formats Title")
    seo_checker_desktop_modern_image_formats_description = fields.Char(string="modern_image_formats Description")
    seo_checker_desktop_modern_image_formats_score = fields.Float(string="modern_image_formats Score")
    seo_checker_desktop_modern_image_formats_diplay_value = fields.Char(string="modern_image_formats Display Value")
    seo_checker_desktop_modern_image_formats_numeric_unit = fields.Char(string="modern_image_formats Numeric Unit")
    seo_checker_desktop_modern_image_formats_item = fields.Char(string="modern_image_formats Item")
    seo_checker_desktop_performance_viewport_title = fields.Char(string="viewport Title")
    seo_checker_desktop_performance_viewport_description = fields.Char(string="viewport Description")
    seo_checker_desktop_performance_viewport_score = fields.Float(string="viewport Score")
    # seo_checker_desktop_largest_contentful_paint_element_title = fields.Char(string="largest_contentful_paint_element Title")
    # seo_checker_desktop_largest_contentful_paint_element_description = fields.Char(string="largest_contentful_paint_element Description")
    # seo_checker_desktop_largest_contentful_paint_element_score = fields.Float(string="largest_contentful_paint_element Score")
    # seo_checker_desktop_largest_contentful_paint_element_diplay_value = fields.Char(string="largest_contentful_paint_element Display Value")
    # seo_checker_desktop_largest_contentful_paint_element_numeric_unit = fields.Char(string="largest_contentful_paint_element Numeric Unit")
    # seo_checker_desktop_largest_contentful_paint_element_item = fields.Char(string="largest_contentful_paint_element Item")
    seo_checker_desktop_uses_optimized_images_title = fields.Char(string="uses_optimized_images Title")
    seo_checker_desktop_uses_optimized_images_description = fields.Char(string="uses_optimized_images Description")
    seo_checker_desktop_uses_optimized_images_score = fields.Float(string="uses_optimized_images Score")
    seo_checker_desktop_uses_optimized_images_item = fields.Char(string="uses_optimized_images Item")
    seo_checker_desktop_uses_responsive_images_title = fields.Char(string="uses_responsive_images Title")
    seo_checker_desktop_uses_responsive_images_description = fields.Char(string="uses_responsive_images Description")
    seo_checker_desktop_uses_responsive_images_score = fields.Float(string="uses_responsive_images Score")
    seo_checker_desktop_uses_responsive_images_display_value = fields.Char(string="uses_responsive_images Display Value")
    seo_checker_desktop_uses_responsive_images_item = fields.Char(string="uses_responsive_images Item")

    seo_checker_mobile_largest_contentful_paint_title = fields.Char(string="largest-contentful-paint Title")
    seo_checker_mobile_largest_contentful_paint_description = fields.Char(string="largest-contentful-paint Description")
    seo_checker_mobile_largest_contentful_paint_score = fields.Float(string="largest-contentful-paint Score")
    seo_checker_mobile_largest_contentful_paint_diplay_value = fields.Char(string="largest-contentful-paint Display Value")
    seo_checker_mobile_largest_contentful_paint_numeric_unit = fields.Char(string="largest-contentful-paint Numeric Unit")
    seo_checker_mobile_total_blocking_time_title = fields.Char(string="total_blocking_time Title")
    seo_checker_mobile_total_blocking_time_description = fields.Char(string="total_blocking_time Description")
    seo_checker_mobile_total_blocking_time_score = fields.Float(string="total_blocking_time Score")
    seo_checker_mobile_total_blocking_time_diplay_value = fields.Char(string="total_blocking_time Display Value")
    seo_checker_mobile_total_blocking_time_numeric_unit = fields.Char(string="total_blocking_time Numeric Unit")
    seo_checker_mobile_cumulative_layout_shift_title = fields.Char(string="cumulative_layout_shift Title")
    seo_checker_mobile_cumulative_layout_shift_description = fields.Char(string="cumulative_layout_shift Description")
    seo_checker_mobile_cumulative_layout_shift_score = fields.Float(string="cumulative_layout_shift Score")
    seo_checker_mobile_cumulative_layout_shift_diplay_value = fields.Char(string="cumulative_layout_shift Display Value")
    seo_checker_mobile_cumulative_layout_shift_numeric_unit = fields.Char(string="cumulative_layout_shift Numeric Unit")
    seo_checker_mobile_speed_index_title = fields.Char(string="speed_index Title")
    seo_checker_mobile_speed_index_description = fields.Char(string="speed_index Description")
    seo_checker_mobile_speed_index_score = fields.Float(string="speed_index Score")
    seo_checker_mobile_speed_index_diplay_value = fields.Char(string="speed_index Display Value")
    seo_checker_mobile_speed_index_numeric_unit = fields.Char(string="speed_index Numeric Unit")
    seo_checker_mobile_interactive_title = fields.Char(string="interactive Title")
    seo_checker_mobile_interactive_description = fields.Char(string="interactive Description")
    seo_checker_mobile_interactive_score = fields.Float(string="interactive Score")
    seo_checker_mobile_interactive_diplay_value = fields.Char(string="interactive Display Value")
    seo_checker_mobile_interactive_numeric_unit = fields.Char(string="interactive Numeric Unit")
    seo_checker_mobile_server_response_time_title = fields.Char(string="server_response_time Title")
    seo_checker_mobile_server_response_time_description = fields.Char(string="server_response_time Description")
    seo_checker_mobile_server_response_time_score = fields.Float(string="server_response_time Score")
    seo_checker_mobile_server_response_time_diplay_value = fields.Char(string="server_response_time Display Value")
    seo_checker_mobile_server_response_time_numeric_unit = fields.Char(string="server_response_time Numeric Unit")
    seo_checker_mobile_total_byte_weight_title = fields.Char(string="total_byte_weight Title")
    seo_checker_mobile_total_byte_weight_description = fields.Char(string="total_byte_weight Description")
    seo_checker_mobile_total_byte_weight_score = fields.Float(string="total_byte_weight Score")
    seo_checker_mobile_total_byte_weight_diplay_value = fields.Char(string="total_byte_weight Display Value")
    seo_checker_mobile_total_byte_weight_numeric_unit = fields.Char(string="total_byte_weight Numeric Unit")
    seo_checker_mobile_render_blocking_resources_title = fields.Char(string="render_blocking_resources Title")
    seo_checker_mobile_render_blocking_resources_description = fields.Char(string="render_blocking_resources Description")
    seo_checker_mobile_render_blocking_resources_score = fields.Float(string="render_blocking_resources Score")
    seo_checker_mobile_render_blocking_resources_diplay_value = fields.Char(string="render_blocking_resources Display Value")
    seo_checker_mobile_render_blocking_resources_numeric_unit = fields.Char(string="render_blocking_resources Numeric Unit")
    seo_checker_mobile_unused_css_rules_title = fields.Char(string="unused_css_rules Title")
    seo_checker_mobile_unused_css_rules_description = fields.Char(string="unused_css_rules Description")
    seo_checker_mobile_unused_css_rules_score = fields.Float(string="unused_css_rules Score")
    seo_checker_mobile_unused_css_rules_diplay_value = fields.Char(string="unused_css_rules Display Value")
    seo_checker_mobile_unused_css_rules_numeric_unit = fields.Char(string="unused_css_rules Numeric Unit")
    seo_checker_mobile_unused_javascript_title = fields.Char(string="unused_javascript Title")
    seo_checker_mobile_unused_javascript_description = fields.Char(string="unused_javascript Description")
    seo_checker_mobile_unused_javascript_score = fields.Float(string="unused_javascript Score")
    seo_checker_mobile_unused_javascript_diplay_value = fields.Char(string="unused_javascript Display Value")
    seo_checker_mobile_unused_javascript_numeric_unit = fields.Char(string="unused_javascript Numeric Unit")
    seo_checker_mobile_duplicated_javascript_title = fields.Char(string="duplicated_javascript Title")
    seo_checker_mobile_duplicated_javascript_description = fields.Char(string="duplicated_javascript Description")
    seo_checker_mobile_duplicated_javascript_score = fields.Float(string="duplicated_javascript Score")
    seo_checker_mobile_duplicated_javascript_diplay_value = fields.Char(string="duplicated_javascript Display Value")
    seo_checker_mobile_duplicated_javascript_numeric_unit = fields.Char(string="duplicated_javascript Numeric Unit")
    seo_checker_mobile_modern_image_formats_title = fields.Char(string="modern_image_formats Title")
    seo_checker_mobile_modern_image_formats_description = fields.Char(string="modern_image_formats Description")
    seo_checker_mobile_modern_image_formats_score = fields.Float(string="modern_image_formats Score")
    seo_checker_mobile_modern_image_formats_diplay_value = fields.Char(string="modern_image_formats Display Value")
    seo_checker_mobile_modern_image_formats_numeric_unit = fields.Char(string="modern_image_formats Numeric Unit")
    seo_checker_mobile_modern_image_formats_item = fields.Char(string="modern_image_formats Item")
    seo_checker_mobile_performance_viewport_title = fields.Char(string="viewport Title")
    seo_checker_mobile_performance_viewport_description = fields.Char(string="viewport Description")
    seo_checker_mobile_performance_viewport_score = fields.Float(string="viewport Score")
    # seo_checker_mobile_largest_contentful_paint_element_title = fields.Char(string="largest_contentful_paint_element Title")
    # seo_checker_mobile_largest_contentful_paint_element_description = fields.Char(string="largest_contentful_paint_element Description")
    # seo_checker_mobile_largest_contentful_paint_element_score = fields.Float(string="largest_contentful_paint_element Score")
    # seo_checker_mobile_largest_contentful_paint_element_diplay_value = fields.Char(string="largest_contentful_paint_element Display Value")
    # seo_checker_mobile_largest_contentful_paint_element_numeric_unit = fields.Char(string="largest_contentful_paint_element Numeric Unit")
    # seo_checker_mobile_largest_contentful_paint_element_item = fields.Char(string="largest_contentful_paint_element Item")
    seo_checker_mobile_uses_optimized_images_title = fields.Char(string="uses_optimized_images Title")
    seo_checker_mobile_uses_optimized_images_description = fields.Char(string="uses_optimized_images Description")
    seo_checker_mobile_uses_optimized_images_score = fields.Float(string="uses_optimized_images Score")
    seo_checker_mobile_uses_optimized_images_item = fields.Char(string="uses_optimized_images Item")
    seo_checker_mobile_uses_responsive_images_title = fields.Char(string="uses_responsive_images Title")
    seo_checker_mobile_uses_responsive_images_description = fields.Char(string="uses_responsive_images Description")
    seo_checker_mobile_uses_responsive_images_score = fields.Float(string="uses_responsive_images Score")
    seo_checker_mobile_uses_responsive_images_display_value = fields.Char(string="uses_responsive_images Display Value")
    seo_checker_mobile_uses_responsive_images_item = fields.Char(string="uses_responsive_images Item")


    seo_fast_extraction_meta_data_response = fields.Char(string="Seo Meta Data Response")
    seo_fast_extraction_links = fields.Char(string="Seo Meta Data Links")
    seo_fast_extraction_headers = fields.Char(string="Seo Meta Data Headers")

    keyword_autosuggest_response = fields.Char(string="Autosuggest Response")
    keyword_autosuggest_recommendations= fields.Char(string="Autosuggest Keyword Recommendation")

    da_pa_and_spam_score_response = fields.Char(string="DA/PA/Spam Response")
    da_score = fields.Float(string="DA Score")
    pa_score = fields.Float(string="PA Score")
    spam_score = fields.Float(string="Spam Score")

    seox_on_page_seo_response = fields.Char(string="On page Seo Response")
    
    google_seo_keyword_research_ai_response = fields.Char(string="Comprehensive Keyword Response")
    google_seo_keyword_research_ai_recommendations = fields.Char(string="Comprehensive Keyword Recommendations")

    keyword_suggestion_api_response = fields.Char(string="Keyword Suggestion Api Response")
    keyword_suggestion_api_recommendations = fields.Char(string="Keyword Suggestion Api Recommendations")

    google_api_web_search_response = fields.Char(string="Web Search Response")
    google_api_keyword_suggestion_response = fields.Char(string="Keyword Suggestion Response")

    scrapingant_response = fields.Char(string="Website Source Code Response")
    scraper_tech_response = fields.Char(string="Screenshot Response")
    regim_response = fields.Char(string="Regim Response")
    trendy_categories_response = fields.Char(string="Categories Response")
    trendy_geographic_response = fields.Char(string="Geographic Response")
    trendy_suggest_response = fields.Char(string="Suggest Response")
    trendy_related_queries_response = fields.Char(string="Related Queries Response")
    trendy_interest_by_region_response = fields.Char(string="Keyword Interest By Region Response")
    trendy_interest_over_time_response = fields.Char(string="Interest Over Time Response")
    
    
    bigrams_rep = fields.Char(string="Bigrams")
    trigrams_rep = fields.Char(string="Trigrams")
    keywords_rep = fields.Char(string="Keywords")

    website_content = fields.Char(string="Website Content")

    number_of_competitors = fields.Integer(string="Number Of Competitors", compute='compute_count')

    def compute_count(self):
        for record in self:
            record.number_of_competitors = self.env['seochecker.profile'].search_count(
                [('related_main_website.id', '=', self.id)])

    def get_competitors(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Competitors',
            'view_mode': 'tree,form',
            'res_model': 'seochecker.profile',
            'domain': [('related_main_website.id', '=', self.id)],
            'context': "{}"
        }

    def see_seochecker_results(self):
        return { 'name': 'Go to website',
                'res_model': 'ir.actions.act_url',
                'type': 'ir.actions.act_url',
                'target' : 'self',
                'url': ("/seo-results?token=" + str(self.uuid))
        }

    def seo_audit_tool_api(self):
        company = self.env['res.company'].sudo().search([["id","=",1]])
        if self.website == False:
            raise UserError(("Please Insert A Website URL"))
        url = "https://seo-audit-tool-api1.p.rapidapi.com/"
        querystring = {"url":self.website}
        headers = {
            "X-RapidAPI-Key": company.seo_audit_tool_rapid_api_key,
            "X-RapidAPI-Host": company.seo_audit_tool_rapid_api_host
        }
        response = requests.get(url, headers=headers, params=querystring)
        #print(response.json())
        self.write({'seo_audit_tool_api_response': response.json()})
        company.write({'seo_audit_tool_rapid_api_usage_counter': company.seo_audit_tool_rapid_api_usage_counter + 1})
        company.write({'seo_audit_tool_rapid_api_credit_number': company.seo_audit_tool_rapid_api_credit_number - 1})
        if response.json()["data"]["success"] == True and response.json()["data"]["result"]["http"]["status"] == 200:
            self["https_status"] = response.json()["data"]["result"]["http"]["using_https"]
            self["content_size"] = response.json()["data"]["result"]["http"]["contentSize"]["bytes"]
            self["response_time"] = response.json()["data"]["result"]["http"]["responseTime"]
            self["title_data"] = response.json()["data"]["result"]["title"]["data"]
            self["title_length"] = response.json()["data"]["result"]["title"]["length"]
            self["meta_description_data"] = response.json()["data"]["result"]["meta_description"]["data"]
            self["meta_description_length"] = response.json()["data"]["result"]["meta_description"]["length"]
            self["metadata_canonical"] = response.json()["data"]["result"]["metadata_info"]["canonical"]
            self["meta_favicon"] = response.json()["data"]["result"]["metadata_info"]["favicon"]
            self["meta_keywords"] = response.json()["data"]["result"]["metadata_info"]["keywords"]
            self["meta_locale"] = response.json()["data"]["result"]["metadata_info"]["locale"]
            self["meta_site_name"] = response.json()["data"]["result"]["metadata_info"]["site_name"]
            self["meta_site_image"] = response.json()["data"]["result"]["metadata_info"]["site_image"]
            self["page_headings_summary"] = response.json()["data"]["result"]["Page Headings summary"]
            self["word_count_total"] = response.json()["data"]["result"]["word_count"]["total"]
            self["anchor_text_words"] = response.json()["data"]["result"]["word_count"]["Anchor text words"]
            self["anchor_percentage"] = response.json()["data"]["result"]["word_count"]["Anchor Percentage"]
            self["total_links"] = response.json()["data"]["result"]["links_summary"]["Total links"]
            self["links_text"] = response.json()["data"]["result"]["links_summary"]["links"]
            self["images_total_number"] = response.json()["data"]["result"]["images_analysis"]["total"]
            self["images_no_src_tag_number"] = response.json()["data"]["result"]["images_analysis"]["No src tag"]
            self["images_no_alt_tag_number"] = response.json()["data"]["result"]["images_analysis"]["No alt tag"]
            self["images_data_src"] = response.json()["data"]["result"]["images_analysis"]["data"]
            self["images_data_alt"] = response.json()["data"]["result"]["images_analysis"]["data"]
        return True
        #-------------------------------------------------------------------

    def seo_api(self):
        company = self.env['res.company'].sudo().search([["id","=",1]])
        if self.website == False:
            raise UserError(("Please Insert A Website URL"))
        url = "https://seo-api2.p.rapidapi.com/keyword-density-checker"
        querystring = {"url":self.website}
        headers = {
            "X-RapidAPI-Key": company.seo_api_key,
            "X-RapidAPI-Host": company.seo_api_host
        }
        response = requests.get(url, headers=headers, params=querystring)
        #print(response.json())
        self.write({'seo_api_keyword_density_response': response.json()})
        company.write({'seo_api_usage_counter': company.seo_api_usage_counter + 1})
        company.write({'seo_api_credit_number': company.seo_api_credit_number - 1})
        if response.status_code  == 200:
            self["seo_api_detected_keywords"] = response.json()
        return True
        #-------------------------------------------------------------------

    def seo_checker_seo_api(self):
        company = self.env['res.company'].sudo().search([["id","=",1]])
        if self.website == False:
            raise UserError(("Please Insert A Website URL"))
        url = "https://seo-checker2.p.rapidapi.com/analyze-v2"
        querystring = {"url":self.website,"category":"seo","strategy":"desktop"}
        headers = {
            "X-RapidAPI-Key": company.seo_checker_api_key,
            "X-RapidAPI-Host": company.seo_checker_api_host
        }
        response = requests.get(url, headers=headers, params=querystring)
        #print(response.json())
        company.write({'seo_checker_api_usage_counter': company.seo_checker_api_usage_counter + 1})
        company.write({'seo_checker_api_credit_number': company.seo_checker_api_credit_number - 1})
        if response.status_code  == 200 and "result" in response.json():
            self["seo_checker_analyzev2_desktop_response"] = response.json()
            self["seo_checker_desktop_font_size_title"] = response.json()["result"]["audits"]["font-size"]["title"]
            self["seo_checker_desktop_font_size_description"] = response.json()["result"]["audits"]["font-size"]["description"]
            self["seo_checker_desktop_link_text_title"] = response.json()["result"]["audits"]["link-text"]["title"]
            self["seo_checker_desktop_link_text_description"] = response.json()["result"]["audits"]["link-text"]["description"]
            self["seo_checker_desktop_tap_targets_title"] = response.json()["result"]["audits"]["tap-targets"]["title"]
            self["seo_checker_desktop_tap_targets_description"] = response.json()["result"]["audits"]["tap-targets"]["description"]
            self["seo_checker_desktop_http_status_code_title"] = response.json()["result"]["audits"]["http-status-code"]["title"]
            self["seo_checker_desktop_http_status_code_description"] = response.json()["result"]["audits"]["http-status-code"]["description"]
            self["seo_checker_desktop_crawlable_anchors_title"] = response.json()["result"]["audits"]["crawlable-anchors"]["title"]
            self["seo_checker_desktop_crawlable_anchors_description"] = response.json()["result"]["audits"]["crawlable-anchors"]["description"]
            self["seo_checker_desktop_crawlable_anchors_items"] = response.json()["result"]["audits"]["crawlable-anchors"]["details"]["items"]
            self["seo_checker_desktop_is_crawlable_title"] = response.json()["result"]["audits"]["is-crawlable"]["title"]
            self["seo_checker_desktop_is_crawlable_description"] = response.json()["result"]["audits"]["is-crawlable"]["description"]
            self["seo_checker_desktop_meta_description_title"] = response.json()["result"]["audits"]["meta-description"]["title"]
            self["seo_checker_desktop_meta_description_description"] = response.json()["result"]["audits"]["meta-description"]["description"]
            self["seo_checker_desktop_structured_data_title"] = response.json()["result"]["audits"]["structured-data"]["title"]
            self["seo_checker_desktop_structured_data_description"] = response.json()["result"]["audits"]["structured-data"]["description"]
            self["seo_checker_desktop_robots_txt_title"] = response.json()["result"]["audits"]["robots-txt"]["title"]
            self["seo_checker_desktop_robots_txt_description"] = response.json()["result"]["audits"]["robots-txt"]["description"]
            self["seo_checker_desktop_document_title_title"] = response.json()["result"]["audits"]["document-title"]["title"]
            self["seo_checker_desktop_document_title_description"] = response.json()["result"]["audits"]["document-title"]["description"]
            self["seo_checker_desktop_document_title_item"] = response.json()["result"]["audits"]["document-title"]["details"]["items"]
            self["seo_checker_desktop_viewport_title"] = response.json()["result"]["audits"]["viewport"]["title"]
            self["seo_checker_desktop_viewport_description"] = response.json()["result"]["audits"]["viewport"]["description"]
            self["seo_checker_desktop_canonical_title"] = response.json()["result"]["audits"]["canonical"]["title"]
            self["seo_checker_desktop_canonical_description"] = response.json()["result"]["audits"]["canonical"]["description"]
            self["seo_checker_desktop_image_alt_title"] = response.json()["result"]["audits"]["image-alt"]["title"]
            self["seo_checker_desktop_image_alt_description"] = response.json()["result"]["audits"]["image-alt"]["description"]
            self["seo_checker_desktop_image_alt_item"] = response.json()["result"]["audits"]["image-alt"]["details"]["items"]
            self["seo_checker_desktop_plugins_title"] = response.json()["result"]["audits"]["plugins"]["title"]
            self["seo_checker_desktop_plugins_description"] = response.json()["result"]["audits"]["plugins"]["description"]
            self["seo_checker_desktop_hreflang_title"] = response.json()["result"]["audits"]["hreflang"]["title"]
            self["seo_checker_desktop_hreflang_description"] = response.json()["result"]["audits"]["hreflang"]["description"]
            self["seo_checker_screenshot"] = response.json()["result"]["fullPageScreenshot"]["screenshot"]["data"]
            self["seo_checker_seo_score_desktop"] = response.json()["result"]["categories"]["seo"]["score"]
        
        url = "https://seo-checker2.p.rapidapi.com/analyze-v2"
        querystring = {"url":self.website,"category":"seo","strategy":"mobile"}
        headers = {
            "X-RapidAPI-Key": company.seo_checker_api_key,
            "X-RapidAPI-Host": company.seo_checker_api_host
        }
        response = requests.get(url, headers=headers, params=querystring)
        #print(response.json())
        company.write({'seo_checker_api_usage_counter': company.seo_checker_api_usage_counter + 1})
        company.write({'seo_checker_api_credit_number': company.seo_checker_api_credit_number - 1})
        if response.status_code  == 200 and "result" in response.json():
            self["seo_checker_analyzev2_mobile_response"] = response.json()
            self["seo_checker_mobile_font_size_title"] = response.json()["result"]["audits"]["font-size"]["title"]
            self["seo_checker_mobile_font_size_description"] = response.json()["result"]["audits"]["font-size"]["description"]
            self["seo_checker_mobile_link_text_title"] = response.json()["result"]["audits"]["link-text"]["title"]
            self["seo_checker_mobile_link_text_description"] = response.json()["result"]["audits"]["link-text"]["description"]
            self["seo_checker_mobile_tap_targets_title"] = response.json()["result"]["audits"]["tap-targets"]["title"]
            self["seo_checker_mobile_tap_targets_description"] = response.json()["result"]["audits"]["tap-targets"]["description"]
            self["seo_checker_mobile_http_status_code_title"] = response.json()["result"]["audits"]["http-status-code"]["title"]
            self["seo_checker_mobile_http_status_code_description"] = response.json()["result"]["audits"]["http-status-code"]["description"]
            self["seo_checker_mobile_crawlable_anchors_title"] = response.json()["result"]["audits"]["crawlable-anchors"]["title"]
            self["seo_checker_mobile_crawlable_anchors_description"] = response.json()["result"]["audits"]["crawlable-anchors"]["description"]
            self["seo_checker_mobile_crawlable_anchors_items"] = response.json()["result"]["audits"]["crawlable-anchors"]["details"]["items"]
            self["seo_checker_mobile_is_crawlable_title"] = response.json()["result"]["audits"]["is-crawlable"]["title"]
            self["seo_checker_mobile_is_crawlable_description"] = response.json()["result"]["audits"]["is-crawlable"]["description"]
            self["seo_checker_mobile_meta_description_title"] = response.json()["result"]["audits"]["meta-description"]["title"]
            self["seo_checker_mobile_meta_description_description"] = response.json()["result"]["audits"]["meta-description"]["description"]
            self["seo_checker_mobile_structured_data_title"] = response.json()["result"]["audits"]["structured-data"]["title"]
            self["seo_checker_mobile_structured_data_description"] = response.json()["result"]["audits"]["structured-data"]["description"]
            self["seo_checker_mobile_robots_txt_title"] = response.json()["result"]["audits"]["robots-txt"]["title"]
            self["seo_checker_mobile_robots_txt_description"] = response.json()["result"]["audits"]["robots-txt"]["description"]
            self["seo_checker_mobile_document_title_title"] = response.json()["result"]["audits"]["document-title"]["title"]
            self["seo_checker_mobile_document_title_description"] = response.json()["result"]["audits"]["document-title"]["description"]
            self["seo_checker_mobile_document_title_item"] = response.json()["result"]["audits"]["document-title"]["details"]["items"]
            self["seo_checker_mobile_viewport_title"] = response.json()["result"]["audits"]["viewport"]["title"]
            self["seo_checker_mobile_viewport_description"] = response.json()["result"]["audits"]["viewport"]["description"]
            self["seo_checker_mobile_canonical_title"] = response.json()["result"]["audits"]["canonical"]["title"]
            self["seo_checker_mobile_canonical_description"] = response.json()["result"]["audits"]["canonical"]["description"]
            self["seo_checker_mobile_image_alt_title"] = response.json()["result"]["audits"]["image-alt"]["title"]
            self["seo_checker_mobile_image_alt_description"] = response.json()["result"]["audits"]["image-alt"]["description"]
            self["seo_checker_mobile_image_alt_item"] = response.json()["result"]["audits"]["image-alt"]["details"]["items"]
            self["seo_checker_mobile_plugins_title"] = response.json()["result"]["audits"]["plugins"]["title"]
            self["seo_checker_mobile_plugins_description"] = response.json()["result"]["audits"]["plugins"]["description"]
            self["seo_checker_mobile_hreflang_title"] = response.json()["result"]["audits"]["hreflang"]["title"]
            self["seo_checker_mobile_hreflang_description"] = response.json()["result"]["audits"]["hreflang"]["description"]
            self["seo_checker_screenshot"] = response.json()["result"]["fullPageScreenshot"]["screenshot"]["data"]
            self["seo_checker_seo_score_mobile"] = response.json()["result"]["categories"]["seo"]["score"]
        return True
        #-------------------------------------------------------------------

    def seo_checker_performance_api(self):
        company = self.env['res.company'].sudo().search([["id","=",1]])
        if self.website == False:
            raise UserError(("Please Insert A Website URL"))
        url = "https://seo-checker2.p.rapidapi.com/analyze-v2"
        querystring = {"url":self.website,"category":"performance","strategy":"desktop"}
        headers = {
            "X-RapidAPI-Key": company.seo_checker_api_key,
            "X-RapidAPI-Host": company.seo_checker_api_host
        }
        response = requests.get(url, headers=headers, params=querystring)
        #print(response.json())
        company.write({'seo_checker_api_usage_counter': company.seo_checker_api_usage_counter + 1})
        company.write({'seo_checker_api_credit_number': company.seo_checker_api_credit_number - 1})
        if response.status_code  == 200 and "result" in response.json():
            self["seo_checker_performance_analyzev2_desktop_response"] = response.json()
            self["seo_checker_desktop_largest_contentful_paint_title"] = response.json()["result"]["audits"]["largest-contentful-paint"]["title"]
            self["seo_checker_desktop_largest_contentful_paint_description"] = response.json()["result"]["audits"]["largest-contentful-paint"]["description"]
            self["seo_checker_desktop_largest_contentful_paint_score"] = response.json()["result"]["audits"]["largest-contentful-paint"]["score"]
            #self["seo_checker_desktop_largest_contentful_paint_diplay_value"] = response.json()["result"]["audits"]["largest-contentful-paint"]["displayValue"]
            self["seo_checker_desktop_largest_contentful_paint_numeric_unit"] = response.json()["result"]["audits"]["largest-contentful-paint"]["numericValue"]
            self["seo_checker_desktop_total_blocking_time_title"] = response.json()["result"]["audits"]["total-blocking-time"]["title"]
            self["seo_checker_desktop_total_blocking_time_description"] = response.json()["result"]["audits"]["total-blocking-time"]["description"]
            self["seo_checker_desktop_total_blocking_time_score"] = response.json()["result"]["audits"]["total-blocking-time"]["score"]
            #self["seo_checker_desktop_total_blocking_time_diplay_value"] = response.json()["result"]["audits"]["total-blocking-time"]["displayValue"]
            self["seo_checker_desktop_total_blocking_time_numeric_unit"] = response.json()["result"]["audits"]["total-blocking-time"]["numericValue"]
            self["seo_checker_desktop_cumulative_layout_shift_title"] = response.json()["result"]["audits"]["cumulative-layout-shift"]["title"]
            self["seo_checker_desktop_cumulative_layout_shift_description"] = response.json()["result"]["audits"]["cumulative-layout-shift"]["description"]
            self["seo_checker_desktop_cumulative_layout_shift_score"] = response.json()["result"]["audits"]["cumulative-layout-shift"]["score"]
            #self["seo_checker_desktop_cumulative_layout_shift_diplay_value"] = response.json()["result"]["audits"]["cumulative-layout-shift"]["displayValue"]
            self["seo_checker_desktop_cumulative_layout_shift_numeric_unit"] = response.json()["result"]["audits"]["cumulative-layout-shift"]["numericValue"]
            self["seo_checker_desktop_speed_index_title"] = response.json()["result"]["audits"]["speed-index"]["title"]
            self["seo_checker_desktop_speed_index_description"] = response.json()["result"]["audits"]["speed-index"]["description"]
            self["seo_checker_desktop_speed_index_score"] = response.json()["result"]["audits"]["speed-index"]["score"]
            #self["seo_checker_desktop_speed_index_diplay_value"] = response.json()["result"]["audits"]["speed-index"]["displayValue"]
            self["seo_checker_desktop_speed_index_numeric_unit"] = response.json()["result"]["audits"]["speed-index"]["numericValue"]
            self["seo_checker_desktop_interactive_title"] = response.json()["result"]["audits"]["interactive"]["title"]
            self["seo_checker_desktop_interactive_description"] = response.json()["result"]["audits"]["interactive"]["description"]
            self["seo_checker_desktop_interactive_score"] = response.json()["result"]["audits"]["interactive"]["score"]
            #self["seo_checker_desktop_interactive_diplay_value"] = response.json()["result"]["audits"]["interactive"]["displayValue"]
            self["seo_checker_desktop_interactive_numeric_unit"] = response.json()["result"]["audits"]["interactive"]["numericValue"]
            self["seo_checker_desktop_server_response_time_title"] = response.json()["result"]["audits"]["server-response-time"]["title"]
            self["seo_checker_desktop_server_response_time_description"] = response.json()["result"]["audits"]["server-response-time"]["description"]
            self["seo_checker_desktop_server_response_time_score"] = response.json()["result"]["audits"]["server-response-time"]["score"]
            #self["seo_checker_desktop_server_response_time_diplay_value"] = response.json()["result"]["audits"]["server-response-time"]["displayValue"]
            self["seo_checker_desktop_server_response_time_numeric_unit"] = response.json()["result"]["audits"]["server-response-time"]["numericValue"]
            self["seo_checker_desktop_render_blocking_resources_title"] = response.json()["result"]["audits"]["render-blocking-resources"]["title"]
            self["seo_checker_desktop_render_blocking_resources_description"] = response.json()["result"]["audits"]["render-blocking-resources"]["description"]
            self["seo_checker_desktop_render_blocking_resources_score"] = response.json()["result"]["audits"]["render-blocking-resources"]["score"]
            #self["seo_checker_desktop_render_blocking_resources_diplay_value"] = response.json()["result"]["audits"]["render-blocking-resources"]["displayValue"]
            self["seo_checker_desktop_render_blocking_resources_numeric_unit"] = response.json()["result"]["audits"]["render-blocking-resources"]["numericValue"]
            self["seo_checker_desktop_unused_css_rules_title"] = response.json()["result"]["audits"]["unused-css-rules"]["title"]
            self["seo_checker_desktop_unused_css_rules_description"] = response.json()["result"]["audits"]["unused-css-rules"]["description"]
            self["seo_checker_desktop_unused_css_rules_score"] = response.json()["result"]["audits"]["unused-css-rules"]["score"]
            #self["seo_checker_desktop_unused_css_rules_diplay_value"] = response.json()["result"]["audits"]["unused-css-rules"]["displayValue"]
            self["seo_checker_desktop_unused_css_rules_numeric_unit"] = response.json()["result"]["audits"]["unused-css-rules"]["numericValue"]
            self["seo_checker_desktop_unused_javascript_title"] = response.json()["result"]["audits"]["unused-javascript"]["title"]
            self["seo_checker_desktop_unused_javascript_description"] = response.json()["result"]["audits"]["unused-javascript"]["description"]
            self["seo_checker_desktop_unused_javascript_score"] = response.json()["result"]["audits"]["unused-javascript"]["score"]
            #self["seo_checker_desktop_unused_javascript_diplay_value"] = response.json()["result"]["audits"]["unused-javascript"]["displayValue"]
            self["seo_checker_desktop_unused_javascript_numeric_unit"] = response.json()["result"]["audits"]["unused-javascript"]["numericValue"]
            self["seo_checker_desktop_duplicated_javascript_title"] = response.json()["result"]["audits"]["duplicated-javascript"]["title"]
            self["seo_checker_desktop_duplicated_javascript_description"] = response.json()["result"]["audits"]["duplicated-javascript"]["description"]
            self["seo_checker_desktop_duplicated_javascript_score"] = response.json()["result"]["audits"]["duplicated-javascript"]["score"]
            #self["seo_checker_desktop_duplicated_javascript_diplay_value"] = response.json()["result"]["audits"]["duplicated-javascript"]["displayValue"]
            self["seo_checker_desktop_duplicated_javascript_numeric_unit"] = response.json()["result"]["audits"]["duplicated-javascript"]["numericValue"]
            self["seo_checker_desktop_modern_image_formats_title"] = response.json()["result"]["audits"]["modern-image-formats"]["title"]
            self["seo_checker_desktop_modern_image_formats_description"] = response.json()["result"]["audits"]["modern-image-formats"]["description"]
            self["seo_checker_desktop_modern_image_formats_score"] = response.json()["result"]["audits"]["modern-image-formats"]["score"]
            #self["seo_checker_desktop_modern_image_formats_diplay_value"] = response.json()["result"]["audits"]["modern-image-formats"]["displayValue"]
            self["seo_checker_desktop_modern_image_formats_numeric_unit"] = response.json()["result"]["audits"]["modern-image-formats"]["numericValue"]
            self["seo_checker_desktop_performance_viewport_title"] = response.json()["result"]["audits"]["viewport"]["title"]
            self["seo_checker_desktop_performance_viewport_description"] = response.json()["result"]["audits"]["viewport"]["description"]
            self["seo_checker_desktop_performance_viewport_score"] = response.json()["result"]["audits"]["viewport"]["score"]
            # self["seo_checker_desktop_largest_contentful_paint_element_title"] = response.json()["result"]["audits"]["largest-contentful-paint-element"]["title"]
            # self["seo_checker_desktop_largest_contentful_paint_element_description"] = response.json()["result"]["audits"]["largest-contentful-paint-element"]["description"]
            # self["seo_checker_desktop_largest_contentful_paint_element_score"] = response.json()["result"]["audits"]["largest-contentful-paint-element"]["score"]
            # self["seo_checker_desktop_largest_contentful_paint_element_diplay_value"] = response.json()["result"]["audits"]["largest-contentful-paint-element"]["displayValue"]
            # self["seo_checker_desktop_largest_contentful_paint_element_numeric_unit"] = response.json()["result"]["audits"]["largest-contentful-paint-element"]["numericValue"]
            self["seo_checker_desktop_uses_optimized_images_title"] = response.json()["result"]["audits"]["uses-optimized-images"]["title"]
            self["seo_checker_desktop_uses_optimized_images_description"] = response.json()["result"]["audits"]["uses-optimized-images"]["description"]
            self["seo_checker_desktop_uses_optimized_images_score"] = response.json()["result"]["audits"]["uses-optimized-images"]["score"]
            #self["seo_checker_desktop_uses_optimized_images_diplay_value"] = response.json()["result"]["audits"]["uses-optimized-images"]["displayValue"]
            #self["seo_checker_desktop_uses_optimized_images_numeric_unit"] = response.json()["result"]["audits"]["uses-optimized-images"]["numericValue"]
            self["seo_checker_desktop_uses_responsive_images_title"] = response.json()["result"]["audits"]["uses-responsive-images"]["title"]
            self["seo_checker_desktop_uses_responsive_images_description"] = response.json()["result"]["audits"]["uses-responsive-images"]["description"]
            self["seo_checker_desktop_uses_responsive_images_score"] = response.json()["result"]["audits"]["uses-responsive-images"]["score"]
            #self["seo_checker_desktop_uses_responsive_images_display_value"] = response.json()["result"]["audits"]["uses-responsive-images"]["displayValue"]
            #self["seo_checker_desktop_uses_responsive_images_numeric_unit"] = response.json()["result"]["audits"]["uses-responsive-images"]["numericValue"]
            self["seo_checker_performance_score_desktop"] = response.json()["result"]["categories"]["performance"]["score"]
        
        url = "https://seo-checker2.p.rapidapi.com/analyze-v2"
        querystring = {"url":self.website,"category":"performance","strategy":"mobile"}
        headers = {
            "X-RapidAPI-Key": company.seo_checker_api_key,
            "X-RapidAPI-Host": company.seo_checker_api_host
        }
        response = requests.get(url, headers=headers, params=querystring)
        #print(response.json())
        company.write({'seo_checker_api_usage_counter': company.seo_checker_api_usage_counter + 1})
        company.write({'seo_checker_api_credit_number': company.seo_checker_api_credit_number - 1})
        if response.status_code  == 200 and "result" in response.json():
            self["seo_checker_performance_analyzev2_mobile_response"] = response.json()
            self["seo_checker_mobile_largest_contentful_paint_title"] = response.json()["result"]["audits"]["largest-contentful-paint"]["title"]
            self["seo_checker_mobile_largest_contentful_paint_description"] = response.json()["result"]["audits"]["largest-contentful-paint"]["description"]
            self["seo_checker_mobile_largest_contentful_paint_score"] = response.json()["result"]["audits"]["largest-contentful-paint"]["score"]
            #self["seo_checker_mobile_largest_contentful_paint_diplay_value"] = response.json()["result"]["audits"]["largest-contentful-paint"]["displayValue"]
            self["seo_checker_mobile_largest_contentful_paint_numeric_unit"] = response.json()["result"]["audits"]["largest-contentful-paint"]["numericValue"]
            self["seo_checker_mobile_total_blocking_time_title"] = response.json()["result"]["audits"]["total-blocking-time"]["title"]
            self["seo_checker_mobile_total_blocking_time_description"] = response.json()["result"]["audits"]["total-blocking-time"]["description"]
            self["seo_checker_mobile_total_blocking_time_score"] = response.json()["result"]["audits"]["total-blocking-time"]["score"]
            #self["seo_checker_mobile_total_blocking_time_diplay_value"] = response.json()["result"]["audits"]["total-blocking-time"]["displayValue"]
            self["seo_checker_mobile_total_blocking_time_numeric_unit"] = response.json()["result"]["audits"]["total-blocking-time"]["numericValue"]
            self["seo_checker_mobile_cumulative_layout_shift_title"] = response.json()["result"]["audits"]["cumulative-layout-shift"]["title"]
            self["seo_checker_mobile_cumulative_layout_shift_description"] = response.json()["result"]["audits"]["cumulative-layout-shift"]["description"]
            self["seo_checker_mobile_cumulative_layout_shift_score"] = response.json()["result"]["audits"]["cumulative-layout-shift"]["score"]
            #self["seo_checker_mobile_cumulative_layout_shift_diplay_value"] = response.json()["result"]["audits"]["cumulative-layout-shift"]["displayValue"]
            self["seo_checker_mobile_cumulative_layout_shift_numeric_unit"] = response.json()["result"]["audits"]["cumulative-layout-shift"]["numericValue"]
            self["seo_checker_mobile_speed_index_title"] = response.json()["result"]["audits"]["speed-index"]["title"]
            self["seo_checker_mobile_speed_index_description"] = response.json()["result"]["audits"]["speed-index"]["description"]
            self["seo_checker_mobile_speed_index_score"] = response.json()["result"]["audits"]["speed-index"]["score"]
            #self["seo_checker_mobile_speed_index_diplay_value"] = response.json()["result"]["audits"]["speed-index"]["displayValue"]
            self["seo_checker_mobile_speed_index_numeric_unit"] = response.json()["result"]["audits"]["speed-index"]["numericValue"]
            self["seo_checker_mobile_interactive_title"] = response.json()["result"]["audits"]["interactive"]["title"]
            self["seo_checker_mobile_interactive_description"] = response.json()["result"]["audits"]["interactive"]["description"]
            self["seo_checker_mobile_interactive_score"] = response.json()["result"]["audits"]["interactive"]["score"]
            #self["seo_checker_mobile_interactive_diplay_value"] = response.json()["result"]["audits"]["interactive"]["displayValue"]
            self["seo_checker_mobile_interactive_numeric_unit"] = response.json()["result"]["audits"]["interactive"]["numericValue"]
            self["seo_checker_mobile_server_response_time_title"] = response.json()["result"]["audits"]["server-response-time"]["title"]
            self["seo_checker_mobile_server_response_time_description"] = response.json()["result"]["audits"]["server-response-time"]["description"]
            self["seo_checker_mobile_server_response_time_score"] = response.json()["result"]["audits"]["server-response-time"]["score"]
            #self["seo_checker_mobile_server_response_time_diplay_value"] = response.json()["result"]["audits"]["server-response-time"]["displayValue"]
            self["seo_checker_mobile_server_response_time_numeric_unit"] = response.json()["result"]["audits"]["server-response-time"]["numericValue"]
            self["seo_checker_mobile_render_blocking_resources_title"] = response.json()["result"]["audits"]["render-blocking-resources"]["title"]
            self["seo_checker_mobile_render_blocking_resources_description"] = response.json()["result"]["audits"]["render-blocking-resources"]["description"]
            self["seo_checker_mobile_render_blocking_resources_score"] = response.json()["result"]["audits"]["render-blocking-resources"]["score"]
            #self["seo_checker_mobile_render_blocking_resources_diplay_value"] = response.json()["result"]["audits"]["render-blocking-resources"]["displayValue"]
            self["seo_checker_mobile_render_blocking_resources_numeric_unit"] = response.json()["result"]["audits"]["render-blocking-resources"]["numericValue"]
            self["seo_checker_mobile_unused_css_rules_title"] = response.json()["result"]["audits"]["unused-css-rules"]["title"]
            self["seo_checker_mobile_unused_css_rules_description"] = response.json()["result"]["audits"]["unused-css-rules"]["description"]
            self["seo_checker_mobile_unused_css_rules_score"] = response.json()["result"]["audits"]["unused-css-rules"]["score"]
            #self["seo_checker_mobile_unused_css_rules_diplay_value"] = response.json()["result"]["audits"]["unused-css-rules"]["displayValue"]
            self["seo_checker_mobile_unused_css_rules_numeric_unit"] = response.json()["result"]["audits"]["unused-css-rules"]["numericValue"]
            self["seo_checker_mobile_unused_javascript_title"] = response.json()["result"]["audits"]["unused-javascript"]["title"]
            self["seo_checker_mobile_unused_javascript_description"] = response.json()["result"]["audits"]["unused-javascript"]["description"]
            self["seo_checker_mobile_unused_javascript_score"] = response.json()["result"]["audits"]["unused-javascript"]["score"]
            #self["seo_checker_mobile_unused_javascript_diplay_value"] = response.json()["result"]["audits"]["unused-javascript"]["displayValue"]
            self["seo_checker_mobile_unused_javascript_numeric_unit"] = response.json()["result"]["audits"]["unused-javascript"]["numericValue"]
            self["seo_checker_mobile_duplicated_javascript_title"] = response.json()["result"]["audits"]["duplicated-javascript"]["title"]
            self["seo_checker_mobile_duplicated_javascript_description"] = response.json()["result"]["audits"]["duplicated-javascript"]["description"]
            self["seo_checker_mobile_duplicated_javascript_score"] = response.json()["result"]["audits"]["duplicated-javascript"]["score"]
            #self["seo_checker_mobile_duplicated_javascript_diplay_value"] = response.json()["result"]["audits"]["duplicated-javascript"]["displayValue"]
            self["seo_checker_mobile_duplicated_javascript_numeric_unit"] = response.json()["result"]["audits"]["duplicated-javascript"]["numericValue"]
            self["seo_checker_mobile_modern_image_formats_title"] = response.json()["result"]["audits"]["modern-image-formats"]["title"]
            self["seo_checker_mobile_modern_image_formats_description"] = response.json()["result"]["audits"]["modern-image-formats"]["description"]
            self["seo_checker_mobile_modern_image_formats_score"] = response.json()["result"]["audits"]["modern-image-formats"]["score"]
            #self["seo_checker_mobile_modern_image_formats_diplay_value"] = response.json()["result"]["audits"]["modern-image-formats"]["displayValue"]
            self["seo_checker_mobile_modern_image_formats_numeric_unit"] = response.json()["result"]["audits"]["modern-image-formats"]["numericValue"]
            self["seo_checker_mobile_performance_viewport_title"] = response.json()["result"]["audits"]["viewport"]["title"]
            self["seo_checker_mobile_performance_viewport_description"] = response.json()["result"]["audits"]["viewport"]["description"]
            self["seo_checker_mobile_performance_viewport_score"] = response.json()["result"]["audits"]["viewport"]["score"]
            # self["seo_checker_mobile_largest_contentful_paint_element_title"] = response.json()["result"]["audits"]["largest-contentful-paint-element"]["title"]
            # self["seo_checker_mobile_largest_contentful_paint_element_description"] = response.json()["result"]["audits"]["largest-contentful-paint-element"]["description"]
            # self["seo_checker_mobile_largest_contentful_paint_element_score"] = response.json()["result"]["audits"]["largest-contentful-paint-element"]["score"]
            # self["seo_checker_mobile_largest_contentful_paint_element_diplay_value"] = response.json()["result"]["audits"]["largest-contentful-paint-element"]["displayValue"]
            # self["seo_checker_mobile_largest_contentful_paint_element_numeric_unit"] = response.json()["result"]["audits"]["largest-contentful-paint-element"]["numericValue"]
            self["seo_checker_mobile_uses_optimized_images_title"] = response.json()["result"]["audits"]["uses-optimized-images"]["title"]
            self["seo_checker_mobile_uses_optimized_images_description"] = response.json()["result"]["audits"]["uses-optimized-images"]["description"]
            self["seo_checker_mobile_uses_optimized_images_score"] = response.json()["result"]["audits"]["uses-optimized-images"]["score"]
            #self["seo_checker_mobile_uses_optimized_images_diplay_value"] = response.json()["result"]["audits"]["uses-optimized-images"]["displayValue"]
            #self["seo_checker_mobile_uses_optimized_images_numeric_unit"] = response.json()["result"]["audits"]["uses-optimized-images"]["numericValue"]
            self["seo_checker_mobile_uses_responsive_images_title"] = response.json()["result"]["audits"]["uses-responsive-images"]["title"]
            self["seo_checker_mobile_uses_responsive_images_description"] = response.json()["result"]["audits"]["uses-responsive-images"]["description"]
            self["seo_checker_mobile_uses_responsive_images_score"] = response.json()["result"]["audits"]["uses-responsive-images"]["score"]
            #self["seo_checker_mobile_uses_responsive_images_display_value"] = response.json()["result"]["audits"]["uses-responsive-images"]["displayValue"]
            #self["seo_checker_mobile_uses_responsive_images_numeric_unit"] = response.json()["result"]["audits"]["uses-responsive-images"]["numericValue"]
            self["seo_checker_performance_score_mobile"] = response.json()["result"]["categories"]["performance"]["score"]
        return True
        #-------------------------------------------------------------------

    def seo_fast_extraction_api(self):
        company = self.env['res.company'].sudo().search([["id","=",1]])
        if self.website == False:
            raise UserError(("Please Insert A Website URL"))
        url = "https://seo-fast-extraction.p.rapidapi.com/"
        querystring = {"url":self.website}
        headers = {
            "X-RapidAPI-Key": company.seo_fast_extraction_key,
            "X-RapidAPI-Host": company.seo_fast_extraction_host
        }
        response = requests.get(url, headers=headers, params=querystring)
        #print(response.json())
        company.write({'seo_fast_extraction_usage_counter': company.seo_fast_extraction_usage_counter + 1})
        company.write({'seo_fast_extraction_credit_number': company.seo_fast_extraction_credit_number - 1})
        if response.status_code  == 200:
            try:
                self["seo_fast_extraction_meta_data_response"] = response.json()
            except:
                pass
            try:
                self["seo_fast_extraction_links"] = response.json()["links"]
            except:
                pass
            try:
                self["seo_fast_extraction_headers"] = response.json()["headers"]
            except:
                pass
        return True
        #-------------------------------------------------------------------

    def keyword_autosuggestion_api(self):
        company = self.env['res.company'].sudo().search([["id","=",1]])
        self["keyword_autosuggest_recommendations"] = False
        url = "https://keyword-autosuggest.p.rapidapi.com/autosuggest"
        kw_list = []
        keyword_list = self.keywords.split(",")
        for keyword in keyword_list:
            querystring = {"q":keyword}
            headers = {
                "X-RapidAPI-Key": company.keyword_autosuggest_key,
                "X-RapidAPI-Host": company.keyword_autosuggest_host
            }
            response = requests.get(url, headers=headers, params=querystring)
            #print(response.json())
            company.write({'keyword_autosuggest_usage_counter': company.keyword_autosuggest_usage_counter + 1})
            company.write({'keyword_autosuggest_credit_number': company.keyword_autosuggest_credit_number - 1})
            if response.status_code  == 200:
                for kw in response.json()["result"]:
                    kw_list.append(kw)
                self["keyword_autosuggest_recommendations"] = str(kw_list)
                self["keyword_autosuggest_response"] = response.json()["result"]
        return True
        #-------------------------------------------------------------------

    def da_pa_spam_api(self):
        company = self.env['res.company'].sudo().search([["id","=",1]])
        if self.website == False:
            raise UserError(("Please Insert A Website URL"))
        self["keyword_autosuggest_recommendations"] = False
        url = "https://da-pa-and-spam-score-api.p.rapidapi.com/check-url"
        payload = { "url": self.website }
        headers = {
            "content-type": "application/json",
            "Content-Type": "application/json",
            "X-RapidAPI-Key": company.da_pa_and_spam_key,
            "X-RapidAPI-Host": company.da_pa_and_spam_host
        }
        response = requests.post(url, json=payload, headers=headers)
        #print(response.json())
        company.write({'da_pa_and_spam_usage_counter': company.da_pa_and_spam_usage_counter + 1})
        company.write({'da_pa_and_spam_credit_number': company.da_pa_and_spam_credit_number - 1})
        if response.status_code  == 200:
            self["da_pa_and_spam_score_response"] = response.json()[0]
            self["da_score"] = response.json()[0]["DA"]
            self["pa_score"] = response.json()[0]["PA"]
            self["spam_score"] = response.json()[0]["Spam Score"]
        return True
        #-------------------------------------------------------------------

    def seox_api(self):
        company = self.env['res.company'].sudo().search([["id","=",1]])
        if self.website == False:
            raise UserError(("Please Insert A Website URL"))
        self["keyword_autosuggest_recommendations"] = False
        url = "https://seox.p.rapidapi.com/api/seo"
        querystring = {"url":self.website}
        headers = {
            "X-RapidAPI-Key": company.seox_key,
            "X-RapidAPI-Host": company.seox_host
        }
        response = requests.get(url, headers=headers, params=querystring)
        #print(response.json())
        company.write({'seox_usage_counter': company.seox_usage_counter + 1})
        company.write({'seox_credit_number': company.seox_credit_number - 1})
        if response.status_code  == 200:
            self["seox_on_page_seo_response"] = response.json()
        return True
        #-------------------------------------------------------------------

    def google_keyword_research_api(self):
        company = self.env['res.company'].sudo().search([["id","=",1]])
        if not self.country_id:
            raise UserError(("Please Insert Research Country"))
        url = "https://google-seo-keyword-research-ai.p.rapidapi.com/keyword-research"
        kw_list = []
        keyword_list = self.keywords.split(",")
        for keyword in keyword_list:
            querystring = {"keyword":keyword,"country":self.country_id.code.lower()}
            headers = {
                "X-RapidAPI-Key": company.google_seo_keyword_research_key,
                "X-RapidAPI-Host": company.google_seo_keyword_research_host
            }
            response = requests.get(url, headers=headers, params=querystring)
            #print(response.json())
            company.write({'google_seo_keyword_research_usage_counter': company.google_seo_keyword_research_usage_counter + 1})
            company.write({'google_seo_keyword_research_credit_number': company.google_seo_keyword_research_credit_number - 1})
            self["google_seo_keyword_research_ai_response"] = response.json()
            if response.status_code  == 200:
                for kw in response.json()["result"]:
                    kw_list.append(kw)
                self["google_seo_keyword_research_ai_recommendations"] = kw_list
                self["google_seo_keyword_research_ai_response"] = response.json()
        return True
        #-------------------------------------------------------------------

    def keyword_suggestion_api(self):
        company = self.env['res.company'].sudo().search([["id","=",1]])
        if self.website == False:
            raise UserError(("Please Insert A Website URL"))
        if not self.country_id:
            raise UserError(("Please Insert Research Country"))
        url = "https://keyword-suggestion-api.p.rapidapi.com/all"
        keyword_list = self.keywords.split(",")
        for keyword in keyword_list:
            querystring = {"keyword":keyword,"language_code":"en","country_code":"us"}
            headers = {
                "X-RapidAPI-Key": company.keyword_suggestion_api_key,
                "X-RapidAPI-Host": company.keyword_suggestion_api_host
            }
            response = requests.get(url, headers=headers, params=querystring)
            #print(response.json())
            company.write({'keyword_suggestion_api_usage_counter': company.keyword_suggestion_api_usage_counter + 1})
            company.write({'keyword_suggestion_api_credit_number': company.keyword_suggestion_api_credit_number - 1})
            if response.status_code  == 200:
                self["keyword_suggestion_api_response"] = response.json()
        return True
        #-------------------------------------------------------------------

    def google_api_keyword(self):
        company = self.env['res.company'].sudo().search([["id","=",1]])
        url = "https://google-api31.p.rapidapi.com/suggestion"
        kw_list = []
        keyword_list = self.keywords.split(",")
        for keyword in keyword_list:
            payload = { "text": keyword.lower() }
            headers = {
                "content-type": "application/json",
                "X-RapidAPI-Key": company.google_api_key,
                "X-RapidAPI-Host": company.google_api_host
            }
            response = requests.post(url, json=payload, headers=headers)
            #print(response.json())
            company.write({'google_api_usage_counter': company.google_api_usage_counter + 1})
            company.write({'google_api_credit_number': company.google_api_credit_number - 1})
            self["google_api_keyword_suggestion_response"] = response.json()
            if response.status_code  == 200:
                for kw in response.json()["result"]:
                    kw_list.append(kw)
                self["google_api_keyword_suggestion_response"] = kw_list
        return True
        #-------------------------------------------------------------------

    def google_api_web_search(self):
        company = self.env['res.company'].sudo().search([["id","=",1]])
        url = "https://google-api31.p.rapidapi.com/websearch"
        kw_list = []
        competitor_id_list = []
        keyword_list = self.keywords.split(",")
        create_ir_logging = self.env['ir.logging'].sudo().create({
                    'dbname': "Last Server",
                    'type': 'server',
                    'name': 'odoo.addons.base.models.ir_actions',
                    'level': 'info',
                    'path': 'action',
                    'line': '489',
                    'func': 'google_api_web_search',
                    'message': str(keyword_list)
                })
        for keyword in keyword_list:
            payload = {
                "text": keyword,
                "safesearch": "off",
                "timelimit": "",
                "region": "en-en",
                "max_results": 5
            }
            headers = {
                "content-type": "application/json",
                "X-RapidAPI-Key": company.google_api_key,
                "X-RapidAPI-Host": company.google_api_host
            }
            response = requests.post(url, json=payload, headers=headers)
            #print(response.json())
            company.write({'google_api_usage_counter': company.google_api_usage_counter + 1})
            company.write({'google_api_credit_number': company.google_api_credit_number - 1})
            self["google_api_web_search_response"] = response.json()
            if response.status_code  == 200:
                for kw in response.json()["result"]:
                    kw_list.append(kw)
                self["google_api_web_search_response"] = kw_list
                unique_uuid = uuid.uuid4()
                for competitor in kw_list:
                    competitor_record = self.env['seochecker.profile'].sudo().search(["&",["website","=",str(competitor["href"])],["related_main_website.id","=",self.id]])
                    if len(competitor_record) == 0:
                        create_competitor = self.env['seochecker.profile'].sudo().create({
                            'name': competitor["href"],
                            'user': self.env.user.id,
                            'website':competitor["href"],
                            'keywords': keyword,
                            'country_id': self.country_id.id,
                            'language_id': self.language_id.id,
                            'uuid': unique_uuid,
                            'related_main_website': self.id
                        })
                        competitor_id_list.append(create_competitor.id)
        self["competitor_websites"] = [(6, 0,competitor_id_list)]
        return True
        #-------------------------------------------------------------------

    def get_contact_of_websites(self):
        company = self.env['res.company'].sudo().search([["id","=",1]])
        if self.website == False:
            raise UserError(("Please Insert A Website URL"))
        if not self.country_id:
            raise UserError(("Please Insert Research Country"))
        url = "https://google-api31.p.rapidapi.com/websearch"
        kw_list = []
        competitor_id_list = []
        keyword_list = self.keywords.split(",")
        create_ir_logging = self.env['ir.logging'].sudo().create({
                    'dbname': "Last Server",
                    'type': 'server',
                    'name': 'odoo.addons.base.models.ir_actions',
                    'level': 'info',
                    'path': 'action',
                    'line': '489',
                    'func': 'google_api_web_search',
                    'message': str(keyword_list)
                })
        for keyword in keyword_list:
            payload = {
                "text": keyword,
                "safesearch": "off",
                "timelimit": "",
                "region": self.country_id.code + "-" + self.country_id.code,
                "max_results": 6
            }
            headers = {
                "content-type": "application/json",
                "X-RapidAPI-Key": company.google_api_key,
                "X-RapidAPI-Host": company.google_api_host
            }
            response = requests.post(url, json=payload, headers=headers)
            #print(response.json())
            company.write({'google_api_usage_counter': company.google_api_usage_counter + 1})
            company.write({'google_api_credit_number': company.google_api_credit_number - 1})
            self["google_api_web_search_response"] = response.json()
            if response.status_code  == 200:
                create_ir_logging = self.env['ir.logging'].sudo().create({
                    'dbname': "Last Server",
                    'type': 'server',
                    'name': 'odoo.addons.base.models.ir_actions',
                    'level': 'info',
                    'path': 'action',
                    'line': '489',
                    'func': 'google_api_web_search',
                    'message': str(response.json())
                })
                for kw in response.json()["result"]:
                    kw_list.append(kw)
                self["google_api_web_search_response"] = kw_list
                unique_uuid = uuid.uuid4()
                for competitor in kw_list:
                    competitor_record = self.env['seochecker.profile'].sudo().search(["&",["website","=",str(competitor["href"])],["related_main_website.id","=",self.id]])
                    if len(competitor_record) == 0:
                        create_competitor = self.env['seochecker.profile'].sudo().create({
                            'name': competitor["href"],
                            'user': self.env.user.id,
                            'website':competitor["href"],
                            'keywords': keyword,
                            'country_id': self.country_id.id,
                            'language_id': self.language_id.id,
                            'uuid': unique_uuid,
                            'related_main_website': self.id
                        })
                        user_agent = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.7) Gecko/2009021910 Firefox/3.0.7'
                        url = create_competitor.website
                        headers={'User-Agent':user_agent,} 
                        #try:
                        request=urllib.request.Request(url,None,headers)
                        response=urllib.request.urlopen(request)
                        if response.getcode() == 200:
                            competitor_id_list.append(create_competitor.id)
                            soup = BeautifulSoup(response.read())
                            create_competitor["website_content"] = self.clean_website_content(str(soup.get_text()))
                        # except urllib.error.URLError as e:
                        #     create_ir_logging = self.env['ir.logging'].sudo().create({
                        #         'dbname': "Last Server",
                        #         'type': 'server',
                        #         'name': 'odoo.addons.base.models.ir_actions',
                        #         'level': 'info',
                        #         'path': 'action',
                        #         'line': '489',
                        #         'func': 'google_api_web_search',
                        #         'message': create_competitor.website + " made error when try to get webspage content"
                        #     })
        self["competitor_websites"] = [(6, 0,competitor_id_list)]
        return True
        #-------------------------------------------------------------------

    def scraper_tech(self):
        company = self.env['res.company'].sudo().search([["id","=",1]])
        if self.website == False:
            raise UserError(("Please Insert A Website URL"))
        if not self.country_id:
            raise UserError(("Please Insert Research Country"))
        url = "https://scraper-tech.p.rapidapi.com/screenshot.php"
        querystring = {"url":self.website}
        payload = {
            "url": self.website,
            "screen_size": "1280x1280",
            "delay": "15",
            "full_height": 1
        }
        headers = {
            "content-type": "application/json",
            "X-RapidAPI-Key": company.scraper_tech_key,
            "X-RapidAPI-Host": company.scraper_tech_host
        }
        response = requests.post(url, json=payload, headers=headers, params=querystring)
        #print(response.json())
        company.write({'scraper_tech_usage_counter': company.scraper_tech_usage_counter + 1})
        company.write({'scraper_tech_credit_number': company.scraper_tech_credit_number - 1})
        self["scraper_tech_response"] = response.json()
        ###########
        ss_url = response.json()['response']['url']
        # _logger.info("*" * 30 + str(ss_url) + "*" * 30)
        downloaded_img = requests.get(ss_url).content
        self.image_of_website = base64.b64encode(downloaded_img)
        ###########
        return True
        #-------------------------------------------------------------------

    def regim(self):
        company = self.env['res.company'].sudo().search([["id","=",1]])
        if self.website == False:
            raise UserError(("Please Insert A Website URL"))
        if not self.country_id:
            raise UserError(("Please Insert Research Country"))
        url = "https://regim3.p.rapidapi.com/1.1/"
        querystring = {"opts":"segmentation,colors"}
        ###########
        decoded_image = base64.b64decode(self.image_of_website)
        with tempfile.NamedTemporaryFile(delete=False, mode="wb", suffix=".jpg") as img_file:
            img_file.write(decoded_image)
        # _logger.info("*" * 30 + img_file.name + "*" * 30)
        files = { "file": open(file=img_file.name, mode="rb") }
        os.remove(img_file.name)
        ###########
        headers = {
            "X-RapidAPI-Key": company.regim_key,
            "X-RapidAPI-Host": company.regim_host
        }
        response = requests.post(url, files=files, headers=headers, params=querystring)
        #print(response.json())
        company.write({'regim_usage_counter': company.regim_usage_counter + 1})
        company.write({'regim_credit_number': company.regim_credit_number - 1})
        self["regim_response"] = response.json()
        return True
        #-------------------------------------------------------------------
    
    
    def seoanalyzer_analyze(self):
        
        output = analyze(url=self.website,follow_links=False)
        # Dissections
        bigrams_to_display = None
        trigrams_to_display = None
        kwords_to_display = None

        for page in output.get("pages"):
            # bigrams dissection
            bigrams = page.get("bigrams")
            if bigrams:
                bg_list = [f'{k}: {v}' for k, v in bigrams.items()]
                bigrams_to_display = ", ".join(bg_list)
            # trigrams dissection
            trigrams = page.get("trigrams")
            if trigrams:
                tg_list = [f'{k}: {v}' for k, v in trigrams.items()]
                trigrams_to_display = ", ".join(tg_list)
            # keywords dissection
            keywords = page.get("keywords")
            if keywords:
                t_list = []
                t_list = [f'{t[1]}: {t[0]}' for t in keywords]
                kwords_to_display = ", ".join(t_list)
                
        self.write({
            'keywords_rep': keywords,
            'bigrams_rep': bigrams,
            'trigrams_rep': trigrams
        })

    def get_website_content(self):
        if self.website == False:
            raise UserError(("Please Insert A Website URL"))
        if not self.country_id:
            raise UserError(("Please Insert Research Country"))
        
        user_agent = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.7) Gecko/2009021910 Firefox/3.0.7'
        url = self.website
        headers={'User-Agent':user_agent,} 
        request=urllib.request.Request(url,None,headers) #The assembled request
        response=urllib.request.urlopen(request)
        if response.getcode() == 200:
            soup = BeautifulSoup(response.read())
            self["website_content"] = self.clean_website_content(str(soup.get_text())[2:-1])
        # user_agent = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.7) Gecko/2009021910 Firefox/3.0.7'

        # url = self.website
        # headers={'User-Agent':user_agent,} 

        # request=urllib.request.Request(url,None,headers) #The assembled request
        # response = urllib.request.urlopen(request)
        # data = response.read() # The data u need
        # self["website_content"] = data
        return True
        #-------------------------------------------------------------------
    
    def clean_website_content(self,string_of_content):
        return string_of_content[2:-1].replace("\\n","").replace("\\t","").replace("  ","")

    # @api.onchange('seochecker_image')
    # def _compute_resized_image(self):
    #     for record in self:
    #         if record.seochecker_image:
    #             # resize uploaded image into 250 X 250
    #             resize_image = tools.image_resize_image(self.seochecker_image, size=(250, 250), avoid_if_small=True)
    
    # @api.model
    # def write(self,vals):
    #     if 'seochecker_image' in vals:
    #         image = tools.ImageProcess(vals['seochecker_image'])
    #         # resize uploaded image into 250 X 250
    #         resize_image = image.resize(350, 350)    
    #         resize_image_b64 = resize_image.image_base64()   
    #         vals['seochecker_image'] = resize_image_b64
    #     if 'image_1' in vals:
    #         image = tools.ImageProcess(vals['image_1'])
    #         # resize uploaded image into 250 X 250
    #         resize_image = image.resize(500, 500)    
    #         resize_image_b64 = resize_image.image_base64()   
    #         vals['image_1'] = resize_image_b64
    #     if 'image_2' in vals:
    #         image = tools.ImageProcess(vals['image_2'])
    #         # resize uploaded image into 250 X 250
    #         resize_image = image.resize(500, 500)    
    #         resize_image_b64 = resize_image.image_base64()   
    #         vals['image_2'] = resize_image_b64
    #     if 'image_3' in vals:
    #         image = tools.ImageProcess(vals['image_3'])
    #         # resize uploaded image into 250 X 250
    #         resize_image = image.resize(500, 500)    
    #         resize_image_b64 = resize_image.image_base64()   
    #         vals['image_3'] = resize_image_b64
    #     obj = super(seocheckerProfile, self).write(vals)
    #     return obj

    # @api.onchange('product_id') 
    # def onchange_by_product(self): 
    #     if self.product_id:
    #         translators = self.env['res.partner'].sudo().search([["language_lines","ilike",self.product_id.name]])
    #         if translators:
    #             return {'domain': {'translator': [('language_lines.product_id.name', 'ilike', self.product_id.name)]}}
            
    # @api.onchange('product_id') 
    # def onchange_by_product_by_translator(self): 
    #     if self.product_id:
    #         self["unit"] = self.product_id.uom_id.category_id.id
    #         products = self.env['product.product'].sudo().search([["default_code","ilike",self.product_id.default_code[0:5]]])
    #         if products:
    #             return {'domain': {'product_id_translator': [('default_code', 'ilike', self.product_id.default_code[0:5])]}}
            
    # @api.onchange('product_id_translator') 
    # def onchange_by_product_id_translator(self): 
    #     if self.product_id_translator:
    #         self["unit_translator"] = self.product_id_translator.uom_id.category_id.id
    #         translators = self.env['res.partner'].sudo().search([["language_lines","ilike",self.product_id_translator.name]])
    #         if translators:
    #             return {'domain': {'translator': [('language_lines.product_id.name', 'ilike', self.product_id_translator.name)]}}

    # @api.onchange('number')
    # def translator_data_calculation(self):
    #     product_found_value = 0
    #     translator = self.translator
    #     for language_line in translator.language_lines:
    #         if language_line.product_id.id == self.product_id.id:
    #             self["sale_price"] = self.product_id.lst_price * self.number
    #             product_found_value = 1
    #     if product_found_value == 0 and len(self.translator):
    #         raise UserError(("Bu Tercüman Seçilen Dil Çevirisi İçin Fiyat Girişi Yapmamış! Tercümanın Profilini Sistemden Bularak Tercüme Fiyatlarını Oluşturunuz.. "))

    # @api.onchange('number')
    # def translator_data_calculation(self):
    #     if self.product_id:
    #         self["sale_price"] = self.product_id.lst_price * self.number
        
    
    # @api.onchange('number_translator')
    # def translator_data_calculation_by_translator(self):
    #     product_found_value = 0
    #     translator = self.translator
    #     for language_line in translator.language_lines:
    #         if language_line.product_id.id == self.product_id_translator.id:
    #             self["translator_unit_price"] = language_line.price
    #             self["translator_unit_price_currency_id"] = language_line.currency_id.id
    #             self["translator_fee"] = language_line.price * self.number_translator
    #             self["translator_price_currency_id"] = language_line.currency_id.id
    #             product_found_value = 1
    #     if product_found_value == 0 and len(self.translator):
    #         self["translator_unit_price"] = 0.0
    #         self["translator_fee"] = 0.0
    #         raise UserError(("Bu Tercüman Seçilen Dil Çevirisi İçin Fiyat Girişi Yapmamış! Tercümanın Profilini Sistemden Bularak Tercüme Fiyatlarını Oluşturunuz.. "))
        


    # def translation_status_confirmed(self):
    #     self.write({'translation_status': 'confirmed'})
    #     return {
	# 	'effect': {
	# 		'fadeout': 'slow',
	# 		'message': 'İşi Onayladın...',
	# 		'type': 'rainbow_man',
	# 	}
	# }

    # def translation_status_started(self):
    #     self.write({'translation_status': 'started'}) 
    #     return {
	# 	'effect': {
	# 		'fadeout': 'slow',
	# 		'message': 'İşi Başlattın Kolay Gelsin...',
	# 		'type': 'rainbow_man',
	# 	}
	# }

    # def translation_status_finished(self):
    #     self.write({'translation_status': 'finished'})
    #     return {
	# 	'effect': {
	# 		'fadeout': 'slow',
	# 		'message': 'Supersin İşi Tamamladın...',
	# 		'type': 'rainbow_man',
	# 	}
	# }

    # def invoice_status_posted(self):
    #     self.write({'invoice_status': 'posted'})
    #     return {
	# 	'effect': {
	# 		'fadeout': 'slow',
	# 		'message': 'Müşteri Faturası Oluşturuldu',
	# 		'type': 'rainbow_man',
	# 	}
	# }

    # def translator_invoice_status_posted(self):
    #     self.write({'translator_invoice_status': 'posted'})
    #     return {
	# 	'effect': {
	# 		'fadeout': 'slow',
	# 		'message': 'Tercüman Faturası Oluşturuldu',
	# 		'type': 'rainbow_man',
	# 	}
	# }
 

    # def tracking_url_open(self):
    #     return { 'name': 'Go to website',
    #             'res_model': 'ir.actions.act_url',
    #             'type': 'ir.actions.act_url',
    #             'target' : 'self',
    #             'url': (str(self.takip_url))
    #            }
    
    # def see_profile(self):
    #     return { 'name': 'Go to website',
    #             'res_model': 'ir.actions.act_url',
    #             'type': 'ir.actions.act_url',
    #             'target' : 'self',
    #             'url': ("/carqr/profile/" + str(self.card_id))
    #            }
    
    # def from_profile(self):
    #     return {
    #         'name':_("Products to Process"),
    #         'view_mode': 'form',
    #         'view_id': False,
    #         'view_type': 'form',
    #         'res_model': 'seochecker.profile',
    #         'res_id': self.id,
    #         'type': 'ir.actions.act_window',
    #         'nodestroy': True,
    #         'target': 'current',
    #         'domain': '[]'
    #     }
        # return { 'name': 'Go to Form Profile',
        #         'res_model': 'ir.actions.act_url',
        #         'type': 'ir.actions.act_url',
        #         'target' : 'self',
        #         'url': ("/web/#id=" + str(119) + "&menu_id=284&action=390&model=seochecker.profile&view_type=form/")
        #        }

    @api.model
    def send_Sms(self,usercode,password,msgheader,gsmno,message):
        url = 'https://api.netgsm.com.tr/sms/send/get?usercode='+ usercode + '&password=' + password + '&msgheader=' + msgheader + '&gsmno=' + gsmno + '&message=' + message
        x = requests.get(url)
        return True
        #-------------------------------------------------------------------


    ################################################
    ################################################
    ## Data Counter Start
    ################################################
    ################################################

    # @api.onchange('source_attachment')
    # def DataCounter_Init_source(self):
    #     _logger = logging.getLogger(__name__)
    #     if self.source_attachment:
    #         file_content = base64.b64decode(self.source_attachment)
    #         with tempfile.NamedTemporaryFile(delete=False) as temp_file:
    #             temp_file.write(file_content)
    #             file_path = temp_file.name
    #         # _logger.info("\n\n\n\n\n" + "X"*50 + "\n\n\n\n\n")
    #         # _logger.info("\n\n\n\n\n" + str(file_path) + "\n\n\n\n\n")
    #         # _logger.info("\n\n\n\n\n" + "X"*50 + "\n\n\n\n\n")
    #         try:
    #             # Call the DataCounter function
    #             word_count, character_count, page_count = self.DataCounter(file_path)
    #             # print(f"Word count: {word_count}")
    #             # print(f"Character count (excluding spaces): {character_count}")
    #             # print(f"Page Count: {page_count}")
    #             # _logger.info("\n\n\n\n\n" + str(self.unit.name) + "\n\n\n\n\n")
    #             if self.unit.id == 	7:
    #                 self.number = character_count
    #             elif self.unit.id == 8:
    #                 self.number = word_count
    #             elif self.unit.id == 9:
    #                 self.number = page_count
                
    #             if self.unit_translator.id == 	7:
    #                 self.number_translator = character_count
    #             elif self.unit_translator.id == 8:
    #                 self.number_translator = word_count
    #             elif self.unit_translator.id == 9:
    #                 self.number_translator = page_count
    #         finally:
    #             # Remove the temporary file
    #             os.remove(file_path)
    
    # @api.onchange('target_attachment')
    # def DataCounter_Init_target(self):
    #     _logger = logging.getLogger(__name__)
    #     if self.source_attachment:
    #         file_content = base64.b64decode(self.target_attachment)
    #         with tempfile.NamedTemporaryFile(delete=False) as temp_file:
    #             temp_file.write(file_content)
    #             file_path = temp_file.name
    #         # _logger.info("\n\n\n\n\n" + "X"*50 + "\n\n\n\n\n")
    #         # _logger.info("\n\n\n\n\n" + str(file_path) + "\n\n\n\n\n")
    #         # _logger.info("\n\n\n\n\n" + "X"*50 + "\n\n\n\n\n")
    #         try:
    #             # Call the DataCounter function
    #             word_count, character_count, page_count = self.DataCounter(file_path)
    #             # print(f"Word count: {word_count}")
    #             # print(f"Character count (excluding spaces): {character_count}")
    #             # print(f"Page Count: {page_count}")
    #             # _logger.info("\n\n\n\n\n" + str(self.unit.name) + "\n\n\n\n\n")
    #             if self.unit.id == 	7:
    #                 self.number = character_count
    #             elif self.unit.id == 8:
    #                 self.number = word_count
    #             elif self.unit.id == 9:
    #                 self.number = page_count

    #             if self.unit_translator.id == 	7:
    #                 self.number_translator = character_count
    #             elif self.unit_translator.id == 8:
    #                 self.number_translator = word_count
    #             elif self.unit_translator.id == 9:
    #                 self.number_translator = page_count
                
    #         finally:
    #             # Remove the temporary file
    #             os.remove(file_path)
    
    
    # def DataCounter(self, file_path):
    #     file_ext = self.DetermineFileSuffix(file_path)
    #     # _logger = logging.getLogger(__name__)
    #     if file_ext == 'docx':
    #         text = docx2txt.process(file_path)
    #         word_count = len(text.split())
    #         ch_count_docx2txt = len(text.replace(" ", "")) # Remove all spaces

    #         doc = docx.Document(file_path)
    #         text = ' '.join(p.text for p in doc.paragraphs)
    #         ch_count_re = len(re.sub(r'\s', '', text))  # Remove all spaces
    #         # average of both methods gives me a closer approximation -> 98.5 - 99.98 % accuracy
    #         character_count = (ch_count_re + ch_count_docx2txt) // 2  
            
    #         # Count pages (approximation based on characters)
    #         characters_per_page = 1500  # Adjust this value based on your document layout
    #         page_count = character_count // characters_per_page + 1

    #         return word_count, character_count, page_count

    #     elif file_ext == 'pdf':
    #         text = extract_text(file_path)

    #         word_count = len(re.findall(r'\w+', text))
    #         character_count = len(re.findall(r'\S', text))
    #         page_count = len(re.findall(r'\f', text))

    #         return word_count, character_count, page_count
    
    #     elif file_ext == 'png' or file_ext == 'jpg':
    #         image = Image.open(file_path)
    #         text = pytesseract.image_to_string(image)
            
    #         word_count = len(text.split())
    #         character_count = len(text.replace(" ", ""))  # Count characters excluding spaces
    #         page_count = 1
            
    #         return word_count, character_count, page_count
    #     else:
    #         raise UserError("Dosya uzantısı docx, pdf, png, jpg veya jpeg olmak zorundadır!")   
        
        
    # def DetermineFileSuffix(self, file_path):
    #     mime = magic.Magic(mime=True)
    #     file_type = mime.from_file(file_path)
        
    #     if file_type == 'application/vnd.openxmlformats-officedocument.wordprocessingml.document':
    #         return 'docx'
    #     elif file_type == 'application/pdf':
    #         return 'pdf'
    #     elif file_type == 'image/png':
    #         return 'png'
    #     elif file_type == 'image/jpg' or file_type == 'image/jpeg':
    #         return 'jpg'
    #     else:
    #         return ''
    ################################################
    ################################################
    ## Data Counter End
    ################################################
    ################################################

    # @api.onchange('device_status','device_status_1','device_status_2','device_status_3','device_status_4','device_status_5')
    # def _get_partner(self):
    #     partner = self.env['res.users'].browse(self.env.uid).partner_id
    #     for rec in self: 
    #         rec.last_action_user = partner.id

    # def write_Link_Status_Active(self):
    #     if self.device_update == False:
    #         self.write({'device_status': 'active'})
    #         self.write({'device_update': True})
    #         partner = self.env['res.users'].browse(self.env.uid).partner_id
    #         for rec in self: 
    #             rec.last_action_user = partner.id
    #     else:
    #         raise ValidationError("Cihaz Son Yaptığınız Ayarları Henüz Almadı. 1 Dakika Sonra Tekrar Deneyiniz.")
        
    # def write_Link_Status_Passive(self):
    #     if self.device_update == False:           
    #         pet = self.env['pets.profile'].sudo().search([["device_id.id","=",self.id]],limit=1)
    #         reports_number = 0
    #         reports = self.env['reports.profile'].search(["&","&","&",["device_id.id","=",self.id],["ademco_id","ilike","E602"],["date",">",pet.registration_date],["date","<",datetime.now()]])
    #         temperature_average = 0
    #         temperature_max = 0
    #         temperature_min = 0
    #         humidity_average = 0
    #         humidity_max = 0
    #         humidity_min = 0
    #         oxygen_average = 0
    #         oxygen_max = 0
    #         oxygen_min = 0
    #         bpm_average = 0
    #         bpm_max = 0
    #         bpm_min = 0
    #         if len(reports) > 0:
    #             reports_number = len(reports)
    #             temperature_average = sum(reports.mapped("sensor_1_value")) / reports_number
    #             temperature_max = max(reports.mapped("sensor_1_value"))
    #             temperature_min = min(reports.mapped("sensor_1_value"))
    #             humidity_average = sum(reports.mapped("sensor_2_value")) / reports_number
    #             humidity_max = max(reports.mapped("sensor_2_value"))
    #             humidity_min = min(reports.mapped("sensor_2_value"))
    #             oxygen_average = sum(reports.mapped("sensor_3_value")) / reports_number
    #             oxygen_max = max(reports.mapped("sensor_3_value"))
    #             oxygen_min = min(reports.mapped("sensor_3_value"))
    #             bpm_average = sum(reports.mapped("sensor_4_value")) / reports_number
    #             bpm_max = max(reports.mapped("sensor_4_value"))
    #             bpm_min = min(reports.mapped("sensor_4_value"))
    #         pet['exit_date'] = datetime.now()
    #         pet['temperature'] = 0
    #         pet['device_id'] = False
    #         pet['values_calculation'] = ("*Süreç Boyunca " + str(round(reports_number,2)) + " Adet Rapor Değerlendirildi. \n*Kabin İçinde Minimum Sıcaklık: " + str(round(temperature_min,2)) +  " Maksimum Sıcaklık: " + str(round(temperature_max,2)) + " Ortalama Sıcaklık : " + str(round(temperature_average,2)) 
    #         + " Olarak Değişti. \n*Kabin İçinde Minimum Nem Oranı: %" + str(round(humidity_min,2)) +  " Maksimum Oksijen Oranı: %" + str(round(humidity_max,2)) + " Ortalama Oksijen Oranı : %" + str(round(humidity_average,2)) + " Olarak Değişti. \n*Kabin İçinde Minimum Oksijen Oranı: %" + str(round(oxygen_min,2)) +  " Maksimum Oksijen Oranı: %" + str(round(oxygen_max,2)) + " Ortalama Oksijen Oranı : %" + str(round(oxygen_average,2)) 
    #         + " Olarak Değişti. \n*Hasta Kalp Atışı; Minimum Bpm: " + str(round(bpm_min,2)) +  " Maksimum Bpm: " + str(round(bpm_max,2)) + " Ortalama Bpm: " + str(round(bpm_average,2)) + " Olarak Değişti.")
    #         self.write({'device_status': 'passive'})
    #         self.write({'device_update': True})
    #         self.write({'pet_id': False})
    #         partner = self.env['res.users'].browse(self.env.uid).partner_id
    #         for rec in self: 
    #             rec.last_action_user = partner.id
    #     else:
    #         raise ValidationError("Cihaz Son Yaptığınız Ayarları Henüz Almadı. 1 Dakika Sonra Tekrar Deneyiniz.")

    # def write_Link_Status_Home(self):
    #     if self.device_update == False:
    #         self.write({'device_status': 'home'})
    #         self.write({'device_update': True})
    #         partner = self.env['res.users'].browse(self.env.uid).partner_id
    #         for rec in self: 
    #             rec.last_action_user = partner.id
    #     else:
    #         raise ValidationError("Cihaz Son Yaptığınız Ayarları Henüz Almadı. 1 Dakika Sonra Tekrar Deneyiniz.")

    # def write_Link_Status_1_Active(self):
    #     if self.device_update == False:
    #         self.write({'device_status_1': 'active'})
    #         self.write({'device_update': True})
    #         partner = self.env['res.users'].browse(self.env.uid).partner_id
    #         for rec in self: 
    #             rec.last_action_user = partner.id
    #     else:
    #         raise ValidationError("Cihaz Son Yaptığınız Ayarları Henüz Almadı. 1 Dakika Sonra Tekrar Deneyiniz.")
        
    # def write_Link_Status_1_Passive(self):
    #     if self.device_update == False:
    #         self.write({'device_status_1': 'passive'})
    #         self.write({'device_update': True})
    #         partner = self.env['res.users'].browse(self.env.uid).partner_id
    #         for rec in self: 
    #             rec.last_action_user = partner.id
    #     else:
    #         raise ValidationError("Cihaz Son Yaptığınız Ayarları Henüz Almadı. 1 Dakika Sonra Tekrar Deneyiniz.")
    
    # def write_Link_Status_2_Active(self):
    #     if self.device_update == False:
    #         self.write({'device_status_2': 'active'})
    #         self.write({'device_update': True})
    #         partner = self.env['res.users'].browse(self.env.uid).partner_id
    #         for rec in self: 
    #             rec.last_action_user = partner.id
    #     else:
    #         raise ValidationError("Cihaz Son Yaptığınız Ayarları Henüz Almadı. 1 Dakika Sonra Tekrar Deneyiniz.")
        
    # def write_Link_Status_2_Passive(self):
    #     if self.device_update == False:
    #         self.write({'device_status_2': 'passive'})
    #         self.write({'device_update': True})
    #         partner = self.env['res.users'].browse(self.env.uid).partner_id
    #         for rec in self: 
    #             rec.last_action_user = partner.id
    #     else:
    #         raise ValidationError("Cihaz Son Yaptığınız Ayarları Henüz Almadı. 1 Dakika Sonra Tekrar Deneyiniz.")
    
    # def write_Link_Status_3_Active(self):
    #     if self.device_update == False:
    #         self.write({'device_status_3': 'active'})
    #         self.write({'device_update': True})
    #         partner = self.env['res.users'].browse(self.env.uid).partner_id
    #         for rec in self: 
    #             rec.last_action_user = partner.id
    #     else:
    #         raise ValidationError("Cihaz Son Yaptığınız Ayarları Henüz Almadı. 1 Dakika Sonra Tekrar Deneyiniz.")
        
    # def write_Link_Status_3_Passive(self):
    #     if self.device_update == False:
    #         self.write({'device_status_3': 'passive'})
    #         self.write({'device_update': True})
    #         partner = self.env['res.users'].browse(self.env.uid).partner_id
    #         for rec in self: 
    #             rec.last_action_user = partner.id
    #     else:
    #         raise ValidationError("Cihaz Son Yaptığınız Ayarları Henüz Almadı. 1 Dakika Sonra Tekrar Deneyiniz.")
    
    # def write_Link_Status_4_Active(self):
    #     if self.device_update == False:
    #         self.write({'device_status_4': 'active'})
    #         self.write({'device_update': True})
    #         partner = self.env['res.users'].browse(self.env.uid).partner_id
    #         for rec in self: 
    #             rec.last_action_user = partner.id
    #     else:
    #         raise ValidationError("Cihaz Son Yaptığınız Ayarları Henüz Almadı. 1 Dakika Sonra Tekrar Deneyiniz.")
        
    # def write_Link_Status_4_Passive(self):
    #     if self.device_update == False:
    #         self.write({'device_status_4': 'passive'})
    #         self.write({'device_update': True})
    #         partner = self.env['res.users'].browse(self.env.uid).partner_id
    #         for rec in self: 
    #             rec.last_action_user = partner.id
    #     else:
    #         raise ValidationError("Cihaz Son Yaptığınız Ayarları Henüz Almadı. 1 Dakika Sonra Tekrar Deneyiniz.")
    
    # def write_Link_Status_5_Active(self):
    #     if self.device_update == False:
    #         self.write({'device_status_5': 'active'})
    #         self.write({'device_update': True})
    #         partner = self.env['res.users'].browse(self.env.uid).partner_id
    #         for rec in self: 
    #             rec.last_action_user = partner.id
    #     else:
    #         raise ValidationError("Cihaz Son Yaptığınız Ayarları Henüz Almadı. 1 Dakika Sonra Tekrar Deneyiniz.")
        
    # def write_Link_Status_5_Passive(self):
    #     if self.device_update == False:
    #         self.write({'device_status_5': 'passive'})
    #         self.write({'device_update': True})
    #         partner = self.env['res.users'].browse(self.env.uid).partner_id
    #         for rec in self: 
    #             rec.last_action_user = partner.id
    #     else:
    #         raise ValidationError("Cihaz Son Yaptığınız Ayarları Henüz Almadı. 1 Dakika Sonra Tekrar Deneyiniz.")
    
    # def create_emergency_report(self):
    #     partner = self.env['res.users'].browse(self.env.uid).partner_id
    #     user_name = "Belirlenemeyen"
    #     for rec in self: 
    #         user_name = partner.name
    #     self.env['reports.profile'].sudo().create({
    #         'name': user_name + " Adlı kullanıcı Acil Durum Çağrısında Bulundu.",
    #         'ademco_id': "B001-000"
    #         })
    # def create_ambulance_report(self):
    #     partner = self.env['res.users'].browse(self.env.uid).partner_id
    #     user_name = "Belirlenemeyen"
    #     for rec in self: 
    #         user_name = partner.name
    #     self.env['reports.profile'].sudo().create({
    #         'name': user_name + " Adlı kullanıcı Ambulans Çağrısında Bulundu.",
    #         'ademco_id': "B002-000"
    #         })
    # def create_fire_report(self):
    #     partner = self.env['res.users'].browse(self.env.uid).partner_id
    #     user_name = "Belirlenemeyen"
    #     for rec in self: 
    #         user_name = partner.name
    #     self.env['reports.profile'].sudo().create({
    #         'name': user_name + " Adlı kullanıcı Yangın Çağrısında Bulundu.",
    #         'ademco_id': "B003-000"
    #         })

    #---------- BİZİM HESAP Start------------------
    @api.model
    def get_bizimhesap(self,url,token):
        header = {'token': token}
        x = requests.get(url,headers = header,timeout=1000)
        data = (x.content)
        decoded_text = self.decode_from_utf8(data)
        create_ir_logging = self.env['ir.logging'].sudo().create({
                    'dbname': "Last Server",
                    'type': 'server',
                    'name': 'odoo.addons.base.models.ir_actions',
                    'level': 'info',
                    'path': 'action',
                    'line': '489',
                    'func': '',
                    'message': decoded_text
                })
        return True
    
    def decode_from_utf8(self, data):
        try:
            udata = data.decode("utf-8", errors='replace')
            return udata
        except UnicodeDecodeError:
            print("Error: Unable to decode the data.")
            return None
        
    @api.model
    def create_bizimhesap_invoice(self,url,json_object):
        headers = {
            "Connection": "keep-alive",
            "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.5 (KHTML, like Gecko) Chrome/19.0.1084.52 Safari/536.5",
            "Content-Type": "application/json"
            }
        myobj = json_object
        x = requests.post(url, json = myobj, headers=headers)
        #print the response text (the content of the requested file):
        #return str(x.content)
        #response = x.json()
        #return str(response['jsonrpc'])
        #aşağıdaki işlemle önce json parse edildi sonra 0-52 ye kadar substring yapıldı
        last_result = json.loads((x.content))
        create_ir_logging = self.env['ir.logging'].sudo().create({
                    'dbname': "Last Server",
                    'type': 'server',
                    'name': 'odoo.addons.base.models.ir_actions',
                    'level': 'info',
                    'path': 'action',
                    'line': '489',
                    'func': 'create_bizimhesap_invoice',
                    'message':  last_result
                })
        return True
        #-------------------------------------------------------------------
        
# class ProductsProductsCustom(models.Model):
#     _inherit = 'products.products'

#     def name_get(self):
#         result = []
#         for record in self:
#             name = f"{record.name} - {record.name}"  # Customize the display name
#             result.append((record.id, name))
#         return result
                              
class ResPartnersInherit(models.Model):
    _inherit = 'res.partner'
    

#discount_percentage = fields.Float("Discount Percentage")

    #gender = fields.Selection([('male','Male'),('female', 'Female'),('other', 'Other'),],string="Gender")
    #type_of_person = fields.Selection([('adult','Adult'),('child', 'Child'),('baby', 'Baby'),('driver', 'Driver')],string="Person Type")
    
    # How to OverRide Create Method Of a Model
    # https://www.youtube.com/watch?v=AS08H3G9x1U&list=PLqRRLx0cl0hoJhjFWkFYowveq2Zn55dhM&index=26
    
    #@api.model
    #def create(self, vals_list):
    #    res = super(ResPartners, self).create(vals_list)
    #    print("yes working")
    #    # do the custom coding here
    #    return res
    