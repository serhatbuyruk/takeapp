# -*- coding: utf-8 -*-

import json
import ast
import random
import logging
import re
import odoo
from odoo import http, _
from odoo.http import request
from odoo.exceptions import AccessError, UserError, AccessDenied
from odoo.osv import expression
from odoo.addons.web.controllers.home import Home
from odoo.addons.website_sale.controllers.main import WebsiteSale
from odoo.addons.website_sale.controllers.variant import WebsiteSaleVariantController
from odoo.addons.auth_oauth.controllers.main import OAuthLogin
from odoo.addons.auth_signup.models.res_users import SignupError
from odoo.addons.website.controllers.main import Website
from odoo.addons.web.controllers.utils import ensure_db

TRUSTED_DEVICE_COOKIE = 'td_alan_id'
TRUSTED_DEVICE_AGE = 90*86400

_logger = logging.getLogger(__name__)

class AlanAuthSystemExtend(Home):

    @http.route('/get_login_popup', type='json', auth="public", website=True)
    def alan_login_popup(self, **kwargs):
        context = {}
        providers = OAuthLogin.list_providers(self)
        context.update(super().get_auth_signup_config())
        context.update({'providers':providers})
        signup_enabled = request.env['res.users']._get_signup_invitation_scope() == 'b2c'
        reset_password_enabled = request.env['ir.config_parameter'].sudo().get_param('auth_signup.reset_password') == 'True'
        website_logo = request.website.image_url(request.website,'logo')
        context.update({'signup_enabled':signup_enabled ,"reset_password_enabled":reset_password_enabled,'website_logo':website_logo})
        return request.env['ir.ui.view']._render_template("theme_alan.as_shop_login",context)

    @http.route('/alan/login/authenticate', type='json', auth="none")
    def alan_login_authenticate(self, **kwargs):
        ''' Login Authentication '''
        ensure_db()
        request.params['login_success'] = False
        request.params['totp_mail'] = False
        if not request.uid:
            request.update_env(user=odoo.SUPERUSER_ID)
        values = request.params.copy()
        if request.httprequest.method == 'POST':
            try:
                uid = request.session.authenticate(request.db, request.params['login'], request.params['password'])
                request.params['login_success'] = True
                url = request.env(user=uid)['res.users'].browse(uid)._mfa_url()
                if url == '/web/login/totp':
                    user = request.env['res.users'].browse(request.session.pre_uid)
                    cookies = request.httprequest.cookies
                    key = cookies.get(TRUSTED_DEVICE_COOKIE)
                    if key:
                        user_match = request.env['auth_totp.device']._check_credentials_for_uid(
                            scope="browser", key=key, uid=user.id)
                        if user_match:
                            request.session.finalize(request.env)
                            request.redirect(self._login_redirect(request.session.uid, redirect=None))
                            return request.params
                        else:
                            request.params['totp_url'] = True
                            return request.params
                    else:
                        request.params['totp_url'] = True
                        return request.params
                else:
                    return request.params
            except odoo.exceptions.AccessDenied as e:
                if e.args == odoo.exceptions.AccessDenied().args:
                    values['error'] = _("Wrong login/password")
                else:
                    values['error'] = e.args[0]
        if 'login' not in values and request.session.get('auth_login'):
            values['login'] = request.session.get('auth_login')
        return values

    @http.route('/alan/login/redirect', type='json', auth="none")
    def _alan_login_redirect(self, **kwargs):
        login_template = request.env['ir.ui.view']._render_template("theme_alan.as_login_totp")
        return {'template':login_template}

    @http.route('/alan/login/two-factor-authenticate', type='json', auth="none")
    def _alan_login_two_factor(self, **kwargs):
        code = request.params['code']
        values = request.params.copy()
        if not request.session.pre_uid:
            return request.redirect('/web/login')
        user = request.env['res.users'].browse(request.session.pre_uid)
        if user and code:
            try:
                with user._assert_can_auth():
                    user._totp_check(int(re.sub(r'\s', '', code)))
            except odoo.exceptions.AccessDenied as e:
                values['error'] = str(e)
            except ValueError:
                values['error'] = _("Invalid authentication code format.")
            else:
                request.session.finalize(request.env)
                request.update_env(user=request.session.uid)
                request.update_context(**request.session.context)
                # response = request.redirect(self._login_redirect(request.session.uid, redirect=None))
                # response = http.Response()
                if request.params['remember'] == True:
                    name = _("%(browser)s on %(platform)s",
                        browser=request.httprequest.user_agent.browser.capitalize(),
                        platform=request.httprequest.user_agent.platform.capitalize(),
                    )
                    geoip = request.geoip
                    if geoip:
                        name += " (%s, %s)" % (geoip['city'], geoip['country_name'])

                    key = request.env['auth_totp.device']._generate("browser", name)
                    values['key'] = key
                # Crapy workaround for unupdatable Odoo Mobile App iOS (Thanks Apple :@)
                request.session.touch()
        return values

    @http.route('/alan/signup/authenticate',type="json",auth="public")
    def alan_signup_authenticate(self,*args, **kw):
        ''' Signup Authentication '''
        qcontext = super(AlanAuthSystemExtend,self).get_auth_signup_qcontext()
        if 'error' not in qcontext and request.httprequest.method == 'POST':
            try:
                super(AlanAuthSystemExtend,self).do_signup(qcontext)
                return {'signup_success':True}
            except UserError as e:
                qcontext['error'] = e.args[0]
            except (SignupError, AssertionError) as e:
                if request.env['res.users'].sudo().search([('login', '=', qcontext.get('login'))]):
                    qcontext['error'] = _('Another user is already registered using this email address.')
                else:
                    _logger.error("%s", e)
                    qcontext['error'] = _('Could not create a new account.')
        return qcontext

class ThemeAlan(http.Controller):

    @http.route('/select/data/fetch', auth='user', type="http", website=True)
    def select2DataFetch(self, terms=False, searchIn=False, **kwargs):
        results = []
        parent_category = kwargs.get("parent_category", 0)
        website_domain = request.website.website_domain()
        if searchIn:
            searchIn = ast.literal_eval(searchIn)
            for search in searchIn:
                if parent_category:
                    kwargs.get("parent_category", 0)
                    domain = website_domain + [('parent_id','=',int(parent_category)),('name','ilike',terms)]
                    records = request.env[search].search(domain)
                else:
                    domain = website_domain + [('name','ilike',terms)]
                    if search in ["product.template", "blog.post"]:
                        domain += [('is_published','=',True)]
                    records = request.env[search].search(domain)
                for record in records:
                    if search == "product.public.category":
                        if parent_category:
                            data = { 'id':record.id, 'name':record.name, 'modal':search,
                            'img': request.website.image_url(record, "image_256") }
                            results.append(data)
                        else:
                            # if not record.parent_id:
                            data = { 'id':record.id, 'name':record.name, 'modal':search ,
                            'img': request.website.image_url(record, "image_256")}
                            results.append(data)
                    elif search == "blog.post":
                        data = { 'id':record.id, 'name':record.display_name, 'modal':search ,
                                'img': request.website.image_url(record, "author_avatar")}
                        results.append(data)
                    else:
                        data = { 'id':record.id, 'name':record.display_name, 'modal':search ,
                                'img': request.website.image_url(record, "image_256")}
                        results.append(data)
        return json.dumps(results)

    @http.route('/get_template', auth='user', type="json", website=True)
    def getTemplate(self, template, context={}):
        return request.env['ir.ui.view']._render_template(template, context)

    @http.route('/get_select2_data', auth='user', type="json", website=True)
    def getSelect2Data(self, **kwargs):
        model = kwargs.get("model", False)
        if model:
            ids = kwargs.get("record_ids", [0])
            data = request.env[model].browse([int(i) for i in ids])
            if len(data) == 1:
                return {'id':data.id, 'text':data.display_name}
        return False

    @http.route('/get_hotspot_product', auth='public', type="json", website=True)
    def getHotSpotInfo(self, product_tmpl_id=0, style="st1"):
        product_id = request.env['product.template'].sudo().browse(int(product_tmpl_id))


        template = request.env['ir.ui.view']._render_template("theme_alan.as_img_hotspot_product_popover", {
            'product':product_id,
            'style':style,
        })
        return {'template':template}

    @http.route('/save_user_custom_frame', auth='public', type="json", website=True)
    def saveUserFrame(self, frame=False, is_default_frame=False, default_frame_id=False, frame_config=False):
        response = {}
        name = request.env['ir.sequence'].sudo().next_by_code('as.frames.seq')
        if not is_default_frame:
            frame_id = request.env['as.snippet.frame'].create({'name':name, 'snippet_frame':frame, 'snippet_frame_html':frame})
            response.update({'frame':frame_id.id})
        else:
            response.update({'frame':default_frame_id})
        name = request.env['ir.sequence'].sudo().next_by_code('as.frame.config.seq')
        frame_config_id = request.env['as.snippet.frame.config'].create({'name':name,'snippet_frame_config':frame_config})
        response.update({'frame_config':frame_config_id.id})
        return response

    @http.route('/get_snippet_frame', auth='public', type="json", website=True)
    def getSnippetFrame(self, frame_id=False, frame_config=False):
        if frame_id and frame_config:
            frame_config_id = request.env['as.snippet.frame.config'].search([('id','=', int(frame_config))])
            frame = request.env['as.snippet.frame'].search([('id','=', int(frame_id))])
            return {'frame_id':frame.snippet_frame, 'frame_config':frame_config_id.snippet_frame_config}
        return { 'frame_id':False, 'frame_config':False }

    @http.route('/get_default_frame', auth='public', type="json", website=True)
    def getDefaultSnippetFrame(self):
        frame_ids = request.env['as.snippet.frame'].search([])
        template = request.env['ir.ui.view']._render_template("theme_alan.s_default_frame",{'frame_ids':frame_ids})
        return { 'response':template }

    @http.route('/delete_default_frame', auth='public', type="json", website=True)
    def deleteDefaultSnippetFrame(self, frame_id=False):
        if frame_id:
            request.env['as.snippet.frame'].search([('id','=', frame_id)]).unlink()
        return True

    @http.route('/get_record_detail', auth='public', type="json", website=True)
    def getDetailInfo(self, record_id=False, model=False, **kwargs):
        if record_id and model:
            rec_info = request.env[model].browse(record_id)
            if model == "blog.post":
                return {"id": rec_info.id,
                    "display_name":rec_info.display_name,
                    "image": request.website.image_url(rec_info,"author_avatar") }
            else:
                return {"id": rec_info.id,
                    "display_name":rec_info.display_name,
                    "image": request.website.image_url(rec_info,"image_1024") }

    @http.route('/get_records_details', auth='public', type="json", website=True)
    def getDetailsInfos(self, record_ids=[], model=False):
        if record_ids and model:
            record_ids = [int(i) for i in record_ids]
            rec_info = request.env[model].browse(record_ids)
            if model == "blog.post":
                return [{"id": rec.id, "display_name":rec.display_name,
                    "name":rec.name,
                    "image": request.website.image_url(rec,"author_avatar") }
                    for rec in rec_info ]
            else:
                return [{"id": rec.id, "display_name":rec.display_name,
                    "name":rec.name,
                    "image": request.website.image_url(rec,"image_1024") }
                    for rec in rec_info ]

    def sort_records(self, modal, sort, limit, domain, random_record=False):
        if modal in ["product.template", "blog.post"]:
            domain += [('is_published','=',True)]
        if sort:
            records = request.env[modal].search(domain, limit=limit, order=sort)
        else:
            if random_record:
                records = request.env[modal].search(domain)
                rec_lst = [{"id": rec.id, "display_name":rec.display_name,
                    "image": request.website.image_url(rec,"image_1024") }
                    for rec in records ]
                random.shuffle(rec_lst)
                return rec_lst[:16]
            else:
                records = request.env[modal].search(domain, limit=limit )
        return records

    @http.route('/get_quick_record', auth='public', type="json", website=True)
    def getQuickRecords(self, mode=False):
        website = request.website
        limit = 50
        from_date = 182
        website_domain = request.website.website_domain()
        if mode == "get_latest_product":
            limit = 15
            records = self.sort_records('product.template', 'create_date DESC', limit, website_domain)
        elif mode == "get_top_product":
            limit = 15
            records = self.sort_records('product.template', 'product_rating DESC', limit, website_domain)
        elif mode == "get_best_sold_product":
            limit = 15
            records = request.env['product.template']._get_best_seller_product(from_date, website.id, limit)
        elif mode == "_get_parent_category":
            website_domain = website_domain + [('parent_id','=', False)]
            records = self.sort_records('product.public.category', False, limit, website_domain)
        elif mode == "_get_a_to_z_category":
            records = self.sort_records('product.public.category', 'name ASC', limit, website_domain)
        elif mode == "_get_z_to_a_category":
            records = self.sort_records('product.public.category', 'name DESC', limit, website_domain)
        elif mode == "_get_z_to_a_brand":
            records = self.sort_records('as.product.brand', 'name DESC', limit, website_domain)
        elif mode == "_get_a_to_z_brand":
            records = self.sort_records('as.product.brand', 'name ASC', limit, website_domain)
        elif mode == "_get_random_brand":
            return self.sort_records('as.product.brand', False, limit, website_domain, True)
        elif mode == "_get_random_product":
            return self.sort_records('product.template', False, limit, website_domain, True)
        elif mode == "_get_random_category":
            return self.sort_records('product.public.category', False, limit, website_domain, True)
        elif mode == "_get_z_to_a_blog":
            records = self.sort_records('blog.post', 'name DESC', limit, website_domain)
        elif mode == "_get_a_to_z_blog":
            records = self.sort_records('blog.post', 'name ASC', limit, website_domain)
        elif mode == "_get_random_blog":
            return self.sort_records('blog.post', False, limit, website_domain, True)
        return [{"id": product_info.id, "display_name":product_info.display_name,
                "image": request.website.image_url(product_info,"image_1024") }
                for product_info in records ]

    @http.route('/get_mega_snippet_template', auth='public', type="json", website=True)
    def getSnipprtTemplate(self, snippet, record_ids, modal, design_editor, **kw):
        if snippet in ["MegaMenuProduct", "MegaMenuBrand"]:
            active_view = design_editor.get("active_view",'slider');
            col_item = int(design_editor.get("col_item",4));
            slider_config = {}
            if active_view == "slider":
                style = design_editor.get("slider_style",'');
                slider_config = {
                    'slidesPerView': 1.5,
                    'spaceBetween': 20,
                    'pagination': {
                    'el': ".swiper-pagination",
                        'clickable': True,
                    },
                    'breakpoints': {
                        767: {
                        'slidesPerView': 2,
                        },
                        1024: {
                        'slidesPerView': col_item,
                        },
                    },
                    'navigation': {
                        'nextEl': ".swiper-button-next",
                        'prevEl': ".swiper-button-prev",
                    },
                }
                if design_editor.get("auto_slider",False):
                    slider_config.update({'autoplay': {'delay': int(design_editor.get('slider_time',4)) * 1000}})
            else:
                style = design_editor.get("grid_style",'');
                col_item = int(12 / col_item);
            template_id = design_editor.get("template_id",False);
            product_ids = request.env[modal].browse(record_ids)
            context = {'data':product_ids, 'style':style, 'col_item':col_item}
            if design_editor.get("allow_link", False):
                context.update({'allow_link':True})
            template = request.env['ir.ui.view']._render_template(template_id, context)
            return {'template':template, 'slider_config':slider_config}
        elif snippet in ["MegaMenuCategory"]:
            active_view = design_editor.get("active_view",'slider');
            col_item = int(design_editor.get("col_item",4));
            slider_config = {}
            if active_view == "slider":
                style = design_editor.get("slider_style",'as-mm-category-slider_1');
                slider_config = {
                    'slidesPerView': 1.5,
                    'spaceBetween': 20,
                    'pagination': {
                    'el': ".swiper-pagination",
                        'clickable': True,
                    },
                    'breakpoints': {
                        767: {
                        'slidesPerView': 2,
                        },
                        1024: {
                        'slidesPerView': col_item,
                        },
                    },
                    'navigation': {
                        'nextEl': ".swiper-button-next",
                        'prevEl': ".swiper-button-prev",
                    },
                }
                if design_editor.get("auto_slider",False):
                    slider_config.update({'autoplay': {'delay': int(design_editor.get('slider_time',4)) * 1000}})

                cat_ids = request.env[modal].browse(record_ids)
                template_id = design_editor.get("template_id",'theme_alan.m_category_slider');
                context = {'data':cat_ids}
            else:
                style = design_editor.get("grid_style",'as-mm-category-grid_1');
                col_item = int(12 / col_item);
                extra_info = kw.get("extra_info", False)
                template_id = design_editor.get("template_id",'theme_alan.m_category_grid');
                data = {}
                sub_data = {}
                if extra_info:
                    for cats in extra_info:
                        parent_id = request.env[modal].browse(cats['parent'])
                        child_ids = []
                        lst = [int(i) for i in cats['childs']]
                        if len(lst):
                            child_ids = request.env[modal].browse(lst)
                        sub_data.update({parent_id: child_ids})
                    for rec in record_ids:
                        parent_id = request.env[modal].browse([rec])
                        if parent_id in sub_data.keys():
                            data.update({parent_id: sub_data[parent_id]})
                        else:
                            data.update({parent_id: []})
                else:
                    for rec in record_ids:
                        parent_id = request.env[modal].browse([rec])
                        if parent_id in sub_data.keys():
                            data.update({parent_id: sub_data[parent_id]})
                        else:
                            data.update({parent_id: []})
                context = {'data':data}
            context.update({'style':style, 'col_item':col_item})
            template = request.env['ir.ui.view']._render_template(template_id, context)
            return {'template':template, 'slider_config':slider_config}

    @http.route('/remove_records', auth='public', type="json", website=True)
    def getRemoveRecords(self, model, ids):
        request.env[model].browse(ids).unlink()
        return True

    @http.route('/get_frame', auth='public', type="json", website=True)
    def getFrame(self, frame_id=0):
        return request.env["as.snippet.frame"].browse(int(frame_id)).snippet_frame

    @http.route('/get_products_snippet_template', auth='public', type="json", website=True)
    def getProductSnippets(self, **kw):
        snippet_type = kw.get("snippet", False)
        website_domain = request.website.website_domain()
        return_context = {}
        if snippet_type:
            modal = kw.get("modal", "product.template")
            ids = kw.get("record_ids",[0])
            context = {}
            # if snippet_type    products_slider_lst:
            configuration = kw.get("design_editor",{})
            if snippet_type == "BestSellingProduct":
                record_ids = request.env[modal].browse(ids)
                return_context.update({'record_ids':[i.id for i in record_ids]})
            elif snippet_type == "LatestProduct":
                record_ids = request.env['product.template'].search(website_domain, limit=15, order="create_date DESC")
                return_context.update({'record_ids':[i.id for i in record_ids]})
            elif snippet_type == "BrandProduct":
                domain = website_domain + [('product_brand_id', 'in', ids)]
                record_ids = request.env['product.template'].search(domain)
                tab_ids = request.env[modal].browse(ids)
                context.update({'tab_ids':tab_ids})
            elif snippet_type == "CategoryProduct":
                domain = website_domain + [('public_categ_ids', 'in', ids)]
                record_ids = request.env['product.template'].search(domain)
                tab_ids = request.env[modal].browse(ids)
                context.update({'tab_ids':tab_ids})
            else:
                if modal == "blog.post":
                    record_ids = request.env[modal].browse(ids)
                    if not request.env.user._is_internal():
                        record_ids = [blog for blog in record_ids if blog.sudo().is_published == True]
                else:
                    record_ids = request.env[modal].browse(ids)

            template = False
            slider_config = {}
            context.update({'records':record_ids, 'configuration':configuration })
            template = request.env['ir.ui.view']._render_template(configuration.get('template_id'), context)
            # slider config
            return_context.update({'template':template ,'slider_config':slider_config})
            if configuration.get("view",False) == 'slider':
                slider_config.update({
                    'loop':configuration.get("loop"),
                    'spaceBetween': 15,
                    'slidesPerView': configuration.get("default_col_mob"),
                    'navigation': {
                        'nextEl': ".swiper-button-next",
                        'prevEl': ".swiper-button-prev",
                    },
                    'breakpoints': {
                        640: {
                        'slidesPerView': configuration.get("default_col_mob"),
                        },
                        768: {
                        'slidesPerView': configuration.get("default_col_mob"),
                        },
                        1024: {
                        'slidesPerView': configuration.get("default_col_desk"),
                        },
                        1200: {
                        'slidesPerView': configuration.get("default_col_desk"),
                        },
                    },
                    'observer': True,
                    'observeSlideChildren': True,
                    'observeParents': True,
                })
                if configuration.get("auto_slider"):
                    slider_config.update({
                        'autoplay':{ 'delay': int(configuration.get("slider_time")) * 1000,
                                    'disableOnInteraction':False }
                    })
                if configuration.get("pagination"):
                    pagination_style = {}
                    if configuration.get("pagination") == 'simple':
                        pagination_style = {
                            'el': ".swiper-pagination"
                        }
                    elif configuration.get("pagination") == 'dynamic':
                        pagination_style = {
                            'el': ".swiper-pagination",
                            'dynamicBullets': True,
                        }
                    elif configuration.get("pagination") == 'progress_bar':
                        pagination_style = {
                            'el': ".swiper-pagination",
                            'type': "progressbar",
                        }
                    elif configuration.get("pagination") == 'fraction':
                        pagination_style = {
                            'el': ".swiper-pagination",
                            'type': "fraction",
                        }
                    elif configuration.get("pagination") == 'scroll_bar':
                        pagination_style = {
                            'el': ".swiper-scrollbar",
                            'hide': True,
                        }
                    elif configuration.get("pagination") == 'coverflow':
                        pagination_style = {
                            'el': ".swiper-pagination",
                        }
                        slider_config.update({
                            "effect": "coverflow",
                            "grabCursor": True,
                            "centeredSlides": True,
                        })
                    elif configuration.get("pagination") == 'cards':
                        slider_config.update({
                            "effect": "cards",
                            "grabCursor": True,
                            "centeredSlides": True,
                        })
                    if configuration.get("pagination") == 'scroll_bar':
                        slider_config.update({'scrollbar':pagination_style })
                    else:
                        slider_config.update({'pagination':pagination_style })

                return_context.update({'slider_config':slider_config})
            return return_context

    @http.route('/get_alan_configuration', auth='public', type="json", website=True)
    def get_alan_configuration(self, **kw):
        website = request.website
        data = {
            'active_login_popup':website.active_login_popup,
            'active_mini_cart':website.active_mini_cart,
            'active_scroll_top':website.active_scroll_top,
            'active_b2b_mode':website.active_b2b_mode,

            'active_shop_quick_view': website.active_shop_quick_view,
            'active_shop_rating': website.active_shop_rating,
            'active_shop_similar_product': website.active_shop_similar_product,
            'active_shop_offer_timer': website.active_shop_offer_timer ,
            'active_shop_color_variant': website.active_shop_color_variant,
            'active_shop_stock_info': website.active_shop_stock_info,
            'active_shop_brand_info': website.active_shop_brand_info,
            'active_shop_hover_image':website.active_shop_hover_image,
            'active_shop_label':website.active_shop_label,
            'active_shop_clear_filter':website.active_shop_clear_filter,
            'active_shop_ppg':website.active_shop_ppg,
            'active_stock_only':website.active_stock_only,
            'active_load_more':website.active_load_more,
            'active_tag_filter':website.active_tag_filter,
            'active_brand_filter':website.active_brand_filter,
            'active_rating_filter':website.active_rating_filter,
            'active_attribute_count':website.active_attribute_count,

            'active_attribute_search':website.active_attribute_search,
            'active_product_label':website.active_product_label,
            'active_product_offer_timer':website.active_product_offer_timer,
            'active_product_reference':website.active_product_reference,
            'active_product_category':website.active_product_category,
            'active_product_tag':website.active_product_tag,
            'active_product_brand':website.active_product_brand,
            'active_product_advance_info':website.active_product_advance_info,
            'active_product_variant_info':website.active_product_variant_info,
            'active_product_accessory':website.active_product_accessory,
            'active_product_alternative':website.active_product_alternative,
            'active_product_pager':website.active_product_pager,
            'active_product_sticky':website.active_product_sticky,
            'active_free_shipping':website.active_free_shipping,
            'active_product_bulk_save':website.active_product_bulk_save,


        }
        return data

    @http.route('/set_alan_configuration', auth='public', type="json", website=True)
    def set_alan_configuration(self, is_active, setting):
        request.website.write({ setting: is_active })
        return True

    @http.route(['/alan/hotspot/translation/'], type='json', auth='public', website=True)
    def hotspot_translation(self,**post):
        website =  request.env['website'].sudo().get_current_website()
        default_title_value = post.get('DefaultTitle')
        defaultAttriute = post.get('DefaultAttribute')
        key_data = post.get('key_data')
        languages = request.env['res.lang'].browse(website.env['res.lang'].search([]).ids)
        languages_data = {}
        for lang in languages:
            languages_data[lang.code] = lang.name
        template = request.env['ir.ui.view']._render_template("theme_alan.as_hotspot_tr",{
            'lang_code_name': languages_data,
            'defaultTitle' : default_title_value,
            'defaultAtt' : defaultAttriute,
            'key_data' : key_data
        })
        return template

class AlanWebsiteSale(WebsiteSale):

    @http.route("/get/internal_reference", type="json", auth="public", website=True)
    def get_internel_reference_code(self,**kwargs):
        product_id = kwargs.get("product_id",0)
        if product_id:
            get_product = request.env["product.product"].search([("id","=",int(product_id))])
            return {"sku":get_product.default_code, 'is_not_variant': False}
        return {"sku": "", 'is_not_variant': True}

    @http.route('/advance/info/editor/<model("as.product.extra.info"):offer>', auth='user', type="http", website=True)
    def offer_design(self, offer):
        return request.render('theme_alan.as_product_advance_info_design', {'layout': offer})

    @http.route('/get_advance_info', auth='public', type="json", website=True)
    def get_advance_info(self, advance_info_id):
        offer = request.env['as.product.extra.info'].sudo().search([('id','=',advance_info_id)], limit=1)
        if offer.detail_description:
            return offer.detail_description
        return ""

    @http.route('/get_quick_view', auth='public', type="json", website=True)
    def quick_view(self, **kw):
        product_id = kw.get('product_id')
        domain = expression.AND([request.website.sale_product_domain(), [('id', '=', product_id)]])
        product = request.env['product.template'].search(domain, limit=1)
        if not product:
            return False
        values = self._prepare_product_values(product, category='', search='', **kw)
        return request.env['ir.ui.view']._render_template("theme_alan.as_quick_view", values=values)

    @http.route('/get_mini_cart', auth='public', type="json", website=True)
    def mini_cart(self, **kw):
        context = {'website_sale_order': request.website.sale_get_order()}
        return request.env["ir.ui.view"]._render_template("theme_alan.as_mini_cart", context)

    @http.route('/get_similar_product', auth='public', type="json", website=True)
    def similar_product(self, **kw):
        product_id = kw.get('product_id')
        domain = expression.AND([request.website.sale_product_domain(), [('id', '=', product_id)]])
        product = request.env['product.template'].search(domain, limit=1)
        if not product:
            return False
        else:
            return request.env['ir.ui.view']._render_template("theme_alan.as_similar_product", {'products':product.alternative_product_ids})

    @http.route('/as_clear_cart', type="json", auth="public" , website=True)
    def as_clear_cart(self, **kw):
        order = request.website.sale_get_order()
        order.unlink()
        request.website.sale_reset()
        return {'data': True}

    @http.route([])
    def product(self, product, category='', search='', **kwargs):
        res = super(AlanWebsiteSale, self).product(product, category, search, **kwargs)
        res.qcontext.update({'as_product_detail':True})
        domain = request.website.sale_product_domain() + [('active','=',True), ('website_published','=',True)]
        prod_lst = product.search(domain , order="website_sequence").mapped("id")
        previous_product = next_product = False
        if product.id in prod_lst:
            last_product_idx = len(prod_lst) - 1
            current_product_idx = prod_lst.index(product.id)
            if current_product_idx != last_product_idx:
                next_prod_id = prod_lst[current_product_idx + 1]
                next_product = product.search([('id','=', next_prod_id)])
            if current_product_idx != 0:
                prev_prod_id = prod_lst[current_product_idx - 1]
                previous_product = product.search([('id','=', prev_prod_id)])
            res.qcontext.update({'next_product':next_product,'previous_product':previous_product})
        return res

class AlanWebsiteSearch(Website):

    @http.route([])
    def autocomplete(self, search_type=None, term=None, order=None, limit=5, max_nb_chars=999, options=None):
        res = super(AlanWebsiteSearch, self).autocomplete( search_type, term, order, limit, max_nb_chars, options)
        if search_type == "as_advance_search":
            brands = []
            tags = []
            category = []
            products = []
            for rec in res['results']:
                if rec.get('_fa') == 'brand':
                    brands.append(rec)
                elif rec.get('_fa') == 'tag':
                    tags.append(rec)
                elif rec.get('_fa') == 'fa-folder-o':
                    category.append(rec)
                else:
                    products.append(rec)
            res.update({
                'brands': brands,
                'tags': tags,
                'category': category,
                'products': products,
            })
        return res

class VariantController(WebsiteSaleVariantController):

    @http.route([])
    def get_combination_info_website(self, product_template_id, product_id, combination, add_qty, **kw):
        res = super(VariantController, self).get_combination_info_website(product_template_id, product_id, combination, add_qty, **kw)
        product_variant_id = res.get('product_id', 0)
        product_variant_id = request.env['product.product'].sudo().search([('id','=', product_variant_id)])
        offer_time = False
        if request.website.active_shop_offer_timer:
            offer_time = product_variant_id._get_offer_timing(request.website.get_current_pricelist())
        res.update({'as_offer_timer':offer_time})
        res.update({'default_code':product_variant_id.default_code})
        return res