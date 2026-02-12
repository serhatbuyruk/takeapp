# -*- coding: utf-8 -*-

from odoo import http, _ , fields
from odoo.http import request, route
from werkzeug.exceptions import NotFound
import datetime
import ast
import json
from markupsafe import Markup
from odoo.addons.website_sale.controllers.main import WebsiteSale
from odoo.addons.website_sale.controllers.variant import WebsiteSaleVariantController


class WebsiteSaleAlanVariant(WebsiteSaleVariantController):
    @route()
    def get_combination_info_website(self, *args, **kwargs):
        res = super().get_combination_info_website(*args, **kwargs)
        res.update({'bulk_save': False})
        if "product_id" in res.keys():
            product_id = request.env['product.product'].sudo().browse(res.get("product_id", 0))
            current_pricelist = request.website.get_current_pricelist()
            if current_pricelist:
                pricelist_item_ids = current_pricelist.sudo()._get_applicable_rules(product_id, fields.Date.today())
                template = request.env['ir.ui.view']._render_template("theme_alan.bulk_save_offers",{
                            'product': product_id,
                            'pricelist_item_ids': pricelist_item_ids })
                get_offer_date = product_id._get_offer_timing(current_pricelist)
                res.update({'bulk_save': template, 'date_offer': get_offer_date})
            res.update({'default_code':product_id.default_code})
        return res

class AlanShop(WebsiteSale):

    @http.route()
    def cart_update_json(
        self, product_id, line_id=None, add_qty=None, set_qty=None, display=True,
        product_custom_attribute_values=None, no_variant_attribute_values=None, **kw):

        res = super(AlanShop, self).cart_update_json(
            product_id, line_id=line_id, add_qty=add_qty, set_qty=set_qty, display=display,
            product_custom_attribute_values=product_custom_attribute_values,
            no_variant_attribute_values=no_variant_attribute_values, **kw
        )
        order = request.website.sale_get_order(force_create=True)
        res['theme_alan.as_shipping_view_template'] = request.env['ir.ui.view']._render_template(
            "theme_alan.as_shipping_view_template", {
                'website_sale_order': order,
            }
        )
        return res

    def hide_out_of_stock(self, product):
        combination = product.sudo()._get_first_possible_combination()
        combination = product.sudo()._get_combination_info(combination, add_qty=1)
        product_id = request.env['product.product'].sudo().browse([combination['product_id']])
        website = request.env['website'].get_current_website()
        if not product_id.sudo().allow_out_of_stock_order and  product_id.sudo().with_context(warehouse=website._get_warehouse_available()).free_qty < 1:
            return False
        else:
            return product.id

    def _shop_lookup_products(self, attrib_set, options, post, search, website):
        product_count, details, fuzzy_search_term = website._search_with_fuzzy("products_only", search,
                                                                               limit=None,
                                                                               order=self._get_search_order(post),
                                                                               options=options)
        search_result = details[0].get('results', request.env['product.template']).with_context(bin_size=True)
        only_stock = request.session.get("stock", False)
        if only_stock:
            search_result =  request.env["product.template"].sudo().browse(list([prod_id for prod_id in map(self.hide_out_of_stock, search_result) if prod_id != False]))
        return fuzzy_search_term, product_count, search_result

    @http.route([])
    def shop(self, page=0, category=None, search='', min_price=0.0, max_price=0.0, ppg=False, **post):
        if request.env.user._is_public():
            request.env.user.clear_caches()

        # Set value for new filter
        if ppg:
            request.session['ppg'] = ppg
        else:
            if request.session.get('ppg', False):
                ppg = request.session['ppg']
            else:
                ppg = False

        only_stock = request.session.get("stock", False)
        if post.get("stock", False) == 'active':
            only_stock = True
        elif post.get("stock", False) == 'inactive':
            only_stock = False
        request.session["stock"] = only_stock

        brand_list = request.httprequest.args.getlist('brand')
        tag_list = request.httprequest.args.getlist('tag')
        rating_list = request.httprequest.args.getlist('rating')
        env_context = dict(request.env.context)
        env_context.update({ 'brands':brand_list, 'rating':rating_list, 'tags':tag_list , 'only_stock' :only_stock})
        request.env.context = env_context
        # Call parent method
        res = super(AlanShop, self).shop(page, category, search, min_price, max_price, ppg, **post)
        # Get current website
        website = request.env['website'].get_current_website()
        # Get attribute value
        attrib_list = request.httprequest.args.getlist('attrib')
        attrib_values = [[int(x) for x in v.split("-")] for v in attrib_list if v]
        attrib_set = {v[1] for v in attrib_values}
        # Price Filter
        pricelist = request.env['product.pricelist'].browse(request.session.get('website_sale_current_pl'))
        filter_by_price_enabled = website.is_view_active('website_sale.filter_products_price')
        if filter_by_price_enabled:
            company_currency = website.company_id.currency_id
            if company_currency and pricelist.currency_id:
                conversion_rate = request.env['res.currency']._get_conversion_rate(
                    company_currency, pricelist.currency_id, request.website.company_id, fields.Date.today())
            else:
                conversion_rate = 1
        else:
            conversion_rate = 1

        Category = request.env['product.public.category']
        if category:
            category = Category.search([('id', '=', int(category))], limit=1)
            if not category or not category.can_access_from_current_website():
                raise NotFound()
        else:
            category = Category

        options = self._get_search_options(
            category=category,
            attrib_values=attrib_values,
            pricelist=pricelist,
            min_price=float(min_price),
            max_price=float(max_price),
            conversion_rate=conversion_rate,
            **post
        )

        fuzzy_search_term, product_count, search_product = self._shop_lookup_products(attrib_set, options, post, search, website)

        # Website Brands
        brand_ids = search_product.mapped("product_brand_id")
        brand_set = [int(brand) for brand in brand_list]
        # Website Tags
        tag_ids = search_product.mapped("product_tag_ids")
        tag_set = [int(tag) for tag in tag_list]
        # Website Rating
        rating_max = 1
        if len(search_product.mapped("product_rating")):
            rating_max = int(max(search_product.mapped("product_rating")))  + 1

        rating_set = [int(rating) for rating in rating_list]
        # Filter Count
        variant_count = self._variant_count(search_product, res.qcontext.get('attributes', False))
        rating_count, brand_count, tag_count = self._rbt_count(search_product, brand_ids, tag_ids)

        res.qcontext.update({
            'brands':brand_ids,
            'brand_set': brand_set,
            'tags':tag_ids,
            'tag_set': tag_set,
            'rating_set': rating_set,
            'selected_brands': request.env['as.product.brand'].browse(brand_set),
            'selected_tags' : request.env['product.tag'].browse(tag_set),
            'ratings':rating_max,
            'variant_count':variant_count,
            'rating_count':rating_count,
            'brand_count':brand_count,
            'tag_count':tag_count,
            'as_shop':True,
            'ppg_list':request.env['as.ppg'].search([]),
            'stock_only':request.session["stock"]
        })

        return res

    def _variant_count(self, search_product, attributes):
        ''' Default attribute counter'''
        attr_count = {}
        if attributes:
            attrs_line = request.env['product.template.attribute.line'].search([('product_tmpl_id','in',search_product.ids)])
            for attr in attributes:
                for val in attr.value_ids:
                    attr_count[str(val.id)] = 0
            if attrs_line:
                for each_line in attrs_line:
                    for val in each_line.value_ids:
                        if str(val.id) in attr_count:
                            attr_count[str(val.id)] += 1
        return attr_count

    def _rbt_count(self, search_product, brand_list, tag_list):
        ''' Rating Brand Tag(rbt)counter'''
        brand_count = { str(brand.id) : 0 for brand in brand_list }
        tag_count = { str(tag.id) : 0 for tag in tag_list }
        rating_count = { rating : 0 for rating in range(1,6) }
        for prod in search_product:
            if prod.product_brand_id and prod.product_brand_id in brand_list:
                brand_count[str(prod.product_brand_id.id)] += 1
            if prod.product_tag_ids:
                for tag in prod.product_tag_ids:
                    if str(tag.id) in tag_count:
                        tag_count[str(tag.id)] += 1
            for rat in range(1,6):
                if prod.product_rating >= rat:
                    rating_count[rat] += 1
        return rating_count, brand_count, tag_count

    @http.route(['/shop/brands', '/shop/brands/page/<int:page>'], type='http', auth="public", website=True)
    def BrandPage(self, page=0):
        domain = ['&',('active','=',True), ('website_id', 'in', (False, request.website.id))]
        brands = request.env['as.product.brand'].sudo().search(domain, order="name asc")
        total = brands.sudo().search_count([])
        pager = request.website.pager(
            url='/shop/brands',
            total=total,
            page=page,
            step=35,
        )
        offset = pager['offset']
        brands = brands[offset: offset + 35]
        return request.render("theme_alan.brand_list", {'brands':brands, 'pager': pager})

    @http.route(['/product_queries'], type="json", auth='public', website=True)
    def product_queries(self, **kw):
        user_obj = request.env['res.partner'].sudo().search([['id', '=',request.env.user.partner_id.id]])
        user = request.env.user.sudo()
        produt_date_time_dict = {}
        now = datetime.datetime.now()
        product_id = kw.get('product_id')
        product = request.env['product.template'].sudo().search([('id','=',product_id)])
        product_id = product.id
        inquiry_data = ast.literal_eval(user.inquiry_data or '{}')
        if not inquiry_data:
            context = {'user_id':user_obj.id,'user_name':user_obj.name, 'user_email': user_obj.email}
            return request.env['ir.ui.view']._render_template("theme_alan.as_product_queries",context)
        else:
            if str(product.id) in list(inquiry_data.keys())  and inquiry_data.get(str(product_id)):
                date_time_compare = datetime.datetime.strptime(inquiry_data.get(str(product_id)), "%Y-%m-%d %H:%M:%S.%f")
                if date_time_compare >= now:
                    return False
                else:
                    context = {'user_id':user_obj.id,'user_name':user_obj.name, 'user_email': user_obj.email}
                    return request.env['ir.ui.view']._render_template("theme_alan.as_product_queries",context)
            else:
                context = {'user_id':user_obj.id,'user_name':user_obj.name, 'user_email': user_obj.email}
                return request.env['ir.ui.view']._render_template("theme_alan.as_product_queries",context)

    @http.route(['/send_queries_mail'], type="json", auth='public', website=True)
    def product_queries_send_mail(self,**kw):

        template = request.env.ref('theme_alan.email_template_product_queries')
        partner_id = request.env['res.partner'].sudo().search([['id', '=',kw.get('user_id')]])
        res_config = request.website.inquiry_submit_action
        user_question = kw.get('message')
        user_email =  kw.get('email')
        product_id = kw.get('product_id')
        contact_preference = kw.get('contact_preference')
        product = request.env['product.template'].sudo().search([('id','=',product_id)])

        user = request.env.user.sudo()

        produt_date_time_dict = {}

        now = datetime.datetime.now()
        product_id = product.id
        time_after_24_hours = now + datetime.timedelta(hours=24)
        inquiry_data = ast.literal_eval(user.inquiry_data or '{}')

        if str(product.id) in list(inquiry_data.keys()):
            produt_date_time_update = {str(product_id): str(time_after_24_hours)}
            inquiry_data.update(produt_date_time_update)
            user.inquiry_data = inquiry_data
        else:
            inquiry_data[product_id] = str(time_after_24_hours)
            updated_inquiry_data = json.dumps(inquiry_data)
            user.inquiry_data = updated_inquiry_data

        if contact_preference  == "Both":
            contact_preference = "Email OR Phone"

        crm_description = Markup('<h3>Product Inquiry - Your Assistance Needed</h3><br/><div>Product Name : %s</div><div>Question : %s</div><div>Contact Preference : %s</div>') % (product.name,user_question,contact_preference)
        if res_config == 'crm':
            sales_team_id = request.website.sales_team_id
            sales_person_id = request.website.sales_person_id
            if sales_team_id and sales_person_id:
                request.env['crm.lead'].sudo().create({
                'team_id':sales_team_id.id,
                'name': 'Product Inquiry',
                'email_from': user_email,
                'user_id':sales_person_id.id,
                'partner_id':partner_id.id,
                'description':crm_description,
            })

        if template and res_config == 'email':
            user_id = request.website.sudo().inquiry_recipient_id
            template.sudo().with_context(
                message = user_question,
                product = product.name,
                partner_name = user_id.partner_id.name,
                contact_preference = contact_preference,
                default_force_send=True,
                default_composition_mode='mass_mail',
                default_model='res.partner',
                default_res_ids=user_id.partner_id.ids,
                default_template_id=template.id,
                email_to=user_id.partner_id.email,
                default_is_queries_mail = True
            ).send_mail(res_id=partner_id.id)
