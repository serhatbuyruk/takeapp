/** @odoo-module  alias=theme_alan.AlanWebsite**/

import Dialog from 'web.Dialog';
import * as ajax from "web.ajax";
import publicWidget from 'web.public.widget';
import webTime from "web.time";
import VariantMixin from "website_sale.VariantMixin";
import websiteSearch from '@website/snippets/s_searchbar/000';
import { cartHandlerMixin } from 'website_sale.utils';
import { qweb } from 'web.core';
import { Markup } from 'web.utils';
import {setCookie} from 'web.utils.cookies';
const rpc = require('web.rpc');

var TRUSTED_DEVICE_COOKIE = 'td_alan_id'
var TRUSTED_DEVICE_AGE = 90*86400

var { searchBar } = websiteSearch;
const CombinationVariant = VariantMixin._onChangeCombination;
import hoverableDropdown from 'website.content.menu';
import config from 'web.config';

var TRUSTED_DEVICE_COOKIE = 'td_alan_id'
var TRUSTED_DEVICE_AGE = 90*86400

publicWidget.registry.hoverableDropdown.include({
    _onMouseEnter: function (ev) {
        if (this.editableMode) {
            // Do not handle hover if another dropdown is opened.
            if (this.el.querySelector('.dropdown-toggle.show')) {
                return;
            }
        }
        // The user must click on the dropdown if he is on mobile (no way to
        // hover) or if the dropdown is the extra menu ('+').
        if (config.device.size_class <= config.device.SIZES.SM ||
            ev.currentTarget.classList.contains('o_extra_menu_items')) {
            return;
        }

        if (ev.currentTarget.querySelector('a.dropdown-toggle')){
            Dropdown.getOrCreateInstance(ev.currentTarget.querySelector('a.dropdown-toggle')).show();
        }
        else {
            return;
        }
    },

    _onMouseLeave: function (ev) {
        if (this.editableMode) {
            // Cancel handling from view mode.
            return;
        }
        if (config.device.size_class <= config.device.SIZES.SM ||
            ev.currentTarget.classList.contains('o_extra_menu_items')) {
            return;
        }

        if (ev.currentTarget.querySelector('a.dropdown-toggle')){
            Dropdown.getOrCreateInstance(ev.currentTarget.querySelector('a.dropdown-toggle')).hide();
        }
        else {
            return;
        }
    },
})

publicWidget.registry.alan_global = publicWidget.Widget.extend({
    'selector': '#wrapwrap',
    'events':{
        'change .oe_search_box' : '_onchange_searchbar',
        'click .as_scroll_to_top' : '_scroll2Top',
        'click .swiper-button-prev, .swiper-button-next' : '_stopEvent',
        'scroll': '_scroll2TopVisibility',
    },

    _onchange_searchbar:function(ev){
        $(ev.currentTarget).parents().find("input[name='min_price']").val(0.0)
        $(ev.currentTarget).parents().find("input[name='max_price']").val(0.0)
    },
    _scroll2TopVisibility:function(){
        if(this.$target.scrollTop() > 1000){
            this.$target.find(".as_scroll_to_top").addClass("as_scroll_show");
        }else{
            this.$target.find(".as_scroll_to_top").removeClass("as_scroll_show");
        }
    },
    _stopEvent:function(ev){
        ev.stopPropagation();
    },
    _scroll2Top:function(){
        $("html, body").animate({ scrollTop: 0 }, "slow");
    }
});

let AlanAdvanceInfo = Dialog.extend({
    events: _.extend({}, Dialog.prototype.events, { 'click .as_close': 'close' }),
    init: function (ele, otps) {
        this.advance_info_id = otps.advance_info_id;
        let dialog_props = {
                            backdrop: true,
                            size: 'extra-large',
                            technical: false,
                            renderHeader: false,
                            renderFooter: false,
                        };
        this._super(ele, _.extend(dialog_props, otps));
    },
    willStart: async function () {
        var template = ajax.jsonRpc('/get_advance_info', 'call', { advance_info_id: this.advance_info_id });
        return Promise.all([this._super(...arguments), template]).then((response) => {
            this.$content = $( "<div>" + response[1] + "</div>");
        });
    },
    start: function () {
        $(this.$content).appendTo(this.$el);
        this.trigger_up('widgets_start_request', {
            $target: this.$content,
        });
        return this._super.apply(this, arguments);
    },
});

publicWidget.registry.alan_advance_info = publicWidget.Widget.extend({
    "selector": ".show_advance_product",
    events : {
        "click": "_show_advance_info_dialog"
    },
    _show_advance_info_dialog: function(){
        this.AlanAdvanceInfo = new AlanAdvanceInfo(this, { advance_info_id: parseInt(this.$target.attr("data-info_id")) });
        this.AlanAdvanceInfo.open();
    }
});


publicWidget.registry.alan_color_variant =  publicWidget.Widget.extend({
    selector: ".as_color_variant",
    events : {
        'mouseenter .as_color_variant_img':'_show_color_image',
        'mouseleave .as_color_variant_img':'_show_default_image',
    },
    _show_color_image:function(ev){
        let color_image = $(ev.currentTarget).find("[data-color-image]").attr("data-color-image");
        this.$target.find(".as_product_main_img").attr("src",color_image);
    },
    _show_default_image:function(ev){
        let product_image = this.$target.find("[data-product-image]").attr("data-product-image");
        this.$target.find(".as_product_main_img").attr("src",product_image);
    }
});

let AlanLoginPopup =  Dialog.extend({
    events: _.extend({}, Dialog.prototype.events, {
        'click .as_close':'close',
        'click .loginbtn':'_checkAuthentication',
        'click .haveAccount':'_backToLogin',
        'click .signupbtn':'_userSignup',
        'click .oe_login_buttons_tf':'_userLoginButton',
    }),
    init: function (ele, otps) {
        let dialog_props = {
                            backdrop: true,
                            size: 'extra-large',
                            technical: false,
                            renderHeader: false,
                            renderFooter: false,
                        };
        this._super(ele, _.extend(dialog_props, otps));
    },
    willStart: async function(){
        var template = ajax.jsonRpc('/get_login_popup', 'call', {'test':'test'});
        return Promise.all([this._super(...arguments), template]).then((response) => {
            this.$content = $(response[1]);
            this.$modal.addClass("as-login-modal");
        });
    },

    start: function () {
        $(this.$content).appendTo(this.$el);
        return this._super.apply(this, arguments);
    },

    _checkAuthentication:function(ev){
        var cr = this;
        const login = cr.$el.find("#login").val();
        const password = cr.$el.find("#password").val();

        if(login.trim() != "" && password.trim() != ""){
            ev.preventDefault();
            return cr._rpc({
                route: "/alan/login/authenticate",
                params: { "login":login, "password":password }
            }).then(function (result) {
                if(result["login_success"] == true){
                    if (result["totp_url"] == true){
                        return cr._rpc({
                        route: "/alan/login/redirect",
                        }).then(function (response) {
                            cr.$el.find(".oe_login_form").replaceWith(response['template'])
                        })
                    }
                    else{
                        window.location.reload();
                    }
                }
                else if("error" in result){
                    cr.$el.find("#errormsg").css("display","block").empty().append(result["error"]);
                }
            });
        }
    },

    _userLoginButton:function(ev){
        var cr = this;
        ev.preventDefault();
        const code = cr.$el.find("#totp_token").val();
        var remember = null
        const $checkedremember = this.$('input[name="remember"]:checked');
        if ($checkedremember.length){
            remember = true
        }
        if (code){
            return cr._rpc({
                route: "/alan/login/two-factor-authenticate",
                params: {"code":code,"remember":remember}
            }).then(function (result) {
                if("error" in result){
                    cr.$el.find("#errormsg").css("display","block").empty().append(result["error"]);
                }else{
                    if("key" in result){
                        setCookie(TRUSTED_DEVICE_COOKIE,result["key"],TRUSTED_DEVICE_AGE);
                        location.reload();
                    }
                    location.reload();
                }
            })
        }
    },

    _userSignup:function(ev){
        var cr = this;
        const logins = cr.$el.find("#logins").val();
        const passwords = cr.$el.find("#passwords").val();
        const names = cr.$el.find("#names").val();
        const confirm_passwords = cr.$el.find("#confirm_passwords").val();
        const token = cr.$el.find("#token").val()
        if(logins.trim() != "" && passwords.trim() != ""
            && confirm_passwords.trim() != "" && names.trim() != ""){
            ev.preventDefault();
            return cr._rpc({
                route: "/alan/signup/authenticate",
                params: {
                        "login":logins,
                        "name":names,
                        "password":passwords,
                        "confirm_password":confirm_passwords,
                        "token":token
                    }
            }).then(function (result) {
                if("error" in result){
                    cr.$el.find("#errors").css("display","block").empty().append(result["error"])
                }
                else if(result["signup_success"] == true){
                    window.location.reload();
                }
            });
        }
    },
    _backToLogin:function(){
        this.$el.find("#as-login").click();
    },
});

publicWidget.registry.alan_login_popup = publicWidget.Widget.extend({
    selector: ".as_login_popup",
    events:{
        'click':'_show_login_popup',
    },
    _show_login_popup:function(ev){
        ev.preventDefault();
        this.AlanLoginPopup = new AlanLoginPopup(this, {});
        this.AlanLoginPopup.open();
    }
});

let AlanMiniCart = Dialog.extend({
    events: _.extend({}, Dialog.prototype.events, {
        'click .as_close':'close',
        'click a.js_add_cart_json':'_onUpdateQty',
        'change .js_quantity':'_onChangeQty',
        'click a.js_delete_product':'_onClickRemoveProduct',
        'click .as-cpt-clr-cart':'_asClearCart',
        'click .show_coupon':'_onClickShowCoupon'
    }),
    _onClickShowCoupon: function (ev) {
        $(".show_coupon").hide();
        $('.coupon_form').find("a").replaceWith('<button class="btn btn-secondary a-submit">Apply</a>');
        $('.coupon_form').removeClass('d-none');
    },
    init:function(ele, otps){
        let dialog_props = {
                            backdrop: true,
                            size: 'extra-large',
                            technical: false,
                            renderHeader: false,
                            renderFooter: false,
                        };
        this._super(ele, _.extend(dialog_props, otps));
    },
    willStart: async function () {
        var template = ajax.jsonRpc('/get_mini_cart', 'call', {});
        return Promise.all([this._super(...arguments), template]).then((response) => {
            this.$content = $(response[1]);
            this.$modal.addClass("as-mini-cart-modal");
        });
    },
    _onClickRemoveProduct: function (ev) {
        ev.preventDefault();
        $(ev.currentTarget).siblings().find('.js_quantity').val(0).trigger("change");
    },
    _onUpdateQty: function(ev){
        ev.preventDefault();
        var $link = $(ev.currentTarget);
        var $input = $link.closest('.input-group').find('input');
        var min = parseFloat($input.data('min') || 0);
        var max = parseFloat($input.data('max') || Infinity);
        var previousQty = parseFloat($input.val() || 0, 10);
        var quantity = ($link.has('.fa-minus').length ? -1 : 1) + previousQty;
        var newQty = quantity > min ? (quantity < max ? quantity : max) : min;
        if (newQty !== previousQty) {
            $input.val(newQty).trigger('change');
        }
        return false;
    },
    _onChangeQty: function (ev){
        var cr = this;
        const product_id = $(ev.currentTarget).data('productId');
        const line_id = $(ev.currentTarget).data('lineId');
        const setQty = $(ev.currentTarget).val();
        if(setQty == 0){
            $(ev.currentTarget).parents(".as-mc-media").remove();
        }
        ajax.jsonRpc('/shop/cart/update_json', 'call', {
            product_id: Number(product_id),
            line_id:line_id || undefined,
            add_qty:undefined,
            set_qty:setQty || undefined,
            no_variant_attribute_values:"[]",
            product_custom_attribute_values:"[]",
        }).then(data =>{
            if(data.cart_quantity == undefined){
                cr.$el.find("as_close").trigger("click");
                location.reload();
            }
            else{
                cr.alanUpdateCartNavBar(data);
                cr.$el.find(".as-cart-summary").empty().append(data['website_sale.short_cart_summary']);
                cr.$el.find(".as-shipping-details").empty().append(data['theme_alan.as_shipping_view_template']);

                cr.$el.find(".as-qty").empty().append(data.cart_quantity);
                if(data.cart_quantity == 1){
                    cr.$el.find(".as-qty-sigl-info").empty().append("item");
                }else{
                    cr.$el.find(".as-qty-sigl-info").empty().append("items");
                }
            }
        })
    },
    _asClearCart:function(){
        this._rpc({route: '/as_clear_cart',params: {}}).then(() => {location.reload()});
    },
    alanUpdateCartNavBar(data) {
        var $qtyNavBar = $(".my_cart_quantity");
        _.each($qtyNavBar, function (qty) {
            var $qty = $(qty);
            $qty.parents('li:first').removeClass('d-none');
            $qty.addClass('o_mycart_zoom_animation').delay(300).queue(function () {
                $(this).text(data.cart_quantity);
                $(this).removeClass("o_mycart_zoom_animation").dequeue();
            });
        });
        $(".js_cart_lines").first().before(data['website_sale.cart_lines']).end().remove();
        $(".js_cart_summary").first().before(data['website_sale.short_cart_summary']).end().remove();
        var $head_cart_amt = $(".as_header_cart_amt");
        if($head_cart_amt.length > 0){
            $(".as_header_cart_amt").first().empty().append(webUtils.Markup(
                $(data["website_sale.short_cart_summary"])
                .find("#order_total_untaxed")
                .find(".monetary_field").html()));
        }
    }
})

publicWidget.registry.as_mini_cart = publicWidget.Widget.extend({
    selector: ".as_mini_cart",
    events:{
        'click':'_show_mini_cart',
    },
    _show_mini_cart:function(ev){
        ev.preventDefault();
        this.AlanMiniCart = new AlanMiniCart(this, { });
        this.AlanMiniCart.open();
    }
});



publicWidget.registry.alan_offer_timer =  publicWidget.Widget.extend({
    selector: ".as_offer_timer",
    disabledInEditableMode: false,
    start:function(){
        if(this.$target.attr("data-offer") != undefined && this.$target.attr("data-offer") != 'false'){
            var self = this;
            var asOfferTimer;
            var offerTimer = function(){
                if(!self.editableMode){
                    var offerTime = moment(webTime.str_to_datetime(self.$target.attr("data-offer")));
                    var currTime = moment();
                    var asTime = moment.duration(offerTime - currTime);
                    asTime = moment.duration(asTime.asMilliseconds() - 1000, 'milliseconds');
                    if (asTime.asMilliseconds() < 0 || self.$target.attr("data-offer") == "") {
                        clearInterval(asOfferTimer);
                        self.$target.empty();
                    }else{
                        var days = parseInt(moment.duration(asTime).asDays());
                        var hours = moment.duration(asTime).hours();
                        var minutes = moment.duration(asTime).minutes();
                        var seconds = moment.duration(asTime).seconds();
                        days = days < 10 ? "0" + days : days;
                        hours = hours < 10 ? "0" + hours : hours;
                        minutes = minutes < 10 ? "0" + minutes : minutes;
                        seconds = seconds < 10 ? "0" + seconds : seconds;
                        self.$target.removeClass("d-none");
                        self.$target.empty().html("<ul>\
                            <li>\
                                <label>"+ days +"</label>\
                                <span>Days</span>\
                            </li>\
                            <li>\
                                <label>"+ hours +"</label>\
                                <span>Hours</span>\
                            </li>\
                            <li>\
                                <label>"+ minutes +"</label>\
                                <span>Minutes</span>\
                            </li>\
                            <li>\
                                <label>"+ seconds +"</label>\
                                <span>Seconds</span>\
                            </li>\
                        </ul>");
                    }
                }else{
                    let timer_info = sessionStorage.getItem("as_timer_ids");
                    if(timer_info !=  undefined){
                        let timer_ids = JSON.parse(timer_info)
                        for (const time_id of timer_ids) {
                            clearInterval(time_id);
                        }
                    }
                    self.$target.empty();
                }
            }
            offerTimer();
            asOfferTimer = setInterval(function () { offerTimer() }, 1000);
            let get_timer_info = sessionStorage.getItem("as_timer_ids");
            var get_timer_ids = [];
            if(get_timer_info != undefined){
                get_timer_ids = JSON.parse(get_timer_info);
            }
            if(get_timer_ids.indexOf(asOfferTimer) == -1){
                get_timer_ids.push(asOfferTimer)
                sessionStorage.setItem("as_timer_ids", JSON.stringify(get_timer_ids))
            }
        }
    }
});

VariantMixin._onChangeCombinationIntercalReference = function (ev, $parent, combination) {
    let $as_bulk_save = this.$target.find(".as_bulk_save");
    if(combination.bulk_save != false){
        $as_bulk_save.removeClass("d-none").empty().append($(combination.bulk_save));
    }else{
        $as_bulk_save.addClass("d-none").empty();
    }

    if(combination.date_offer != false ){
        this.$target.find(".as_offer_timer").attr("data-offer",combination.date_offer);
        this.trigger_up('widgets_start_request', {
            $target: $('.as_offer_timer'),
        });
    }else{
        this.$target.find(".as_offer_timer").attr("data-offer","");
    }
}

publicWidget.registry.WebsiteSale.include({
    _onChangeCombination: function (){
        this._super.apply(this, arguments);
        VariantMixin._onChangeCombinationIntercalReference.apply(this, arguments);
        var product_id = arguments[2]['product_id'];
        var product_template_id = arguments[2]['product_template_id'];
        this._rpc({
            route: '/get/internal_reference',
            params: {
                'product_id':product_id,
                'product_tmpl_id':product_template_id
            }
        }).then(function (result) {
            $(".as-internal-code").empty().append(result["sku"]);
            if (result.is_not_variant) {
                $(".as-internal-sku-lable").addClass('d-none')
            }
            else {
                $(".as-internal-sku-lable").removeClass('d-none')
            }
        });
    }
});


publicWidget.registry.as_product_detail_info = publicWidget.Widget.extend({
    selector:".as-product-detail",
    'events':{
        'click a#add_to_cart_cp_btn':'_sticky_add_to_cart',
        'click .as-scroll-top':'_as_scroll_top',
        'click a#buy_now_cp_btn':'_sticky_buy_now',
        'click .o_website_rating_static':'_product_rating',
        'scroll':'_stickyCart',
        'mouseenter .as-pager-prod':'_show_pager_product_info',
        'mouseleave .as-pager-prod':'_hide_pager_product_info',

    },
    start: function () {
        new Swiper(".as-al-ass-swiper", {
            slidesPerView: 1.75,
            spaceBetween: 10,
            navigation: {
              nextEl: ".swiper-button-ass-next",
              prevEl: ".swiper-button-ass-prev",
            },
            breakpoints: {
              640: {
                slidesPerView: 2,
                spaceBetween: 24,
              },
              768: {
                slidesPerView: 3,
                spaceBetween: 24,
              },
              1024: {
                slidesPerView: 4,
                spaceBetween: 24,
              },

            },
        });

        new Swiper(".as-al-alt-swiper", {
            slidesPerView: 1.75,
            spaceBetween: 10,
            navigation: {
              nextEl: ".swiper-button-alt-next",
              prevEl: ".swiper-button-alt-prev",
            },
            breakpoints: {
              640: {
                slidesPerView: 2,
                spaceBetween: 24,
              },
              768: {
                slidesPerView: 3,
                spaceBetween: 24,
              },
              1024: {
                slidesPerView: 4,
                spaceBetween: 24,
              },

            },
        });

        return this._super.apply(this, arguments);
    },
    _show_pager_product_info(ev){

        if($(ev.currentTarget).attr('id') == "as-pre-prod-info"){
            this.$target.find(".as-pre-prod-info").removeClass("d-none");
        }else{
            this.$target.find(".as-next-prod-info").removeClass("d-none");
        }
    },
    _hide_pager_product_info(ev){
        this.$target.find(".as-pager-prod-info").addClass("d-none")
    },
    _sticky_add_to_cart:function(ev){
        const product_id = $(ev.currentTarget).closest("form").find("input[name='product_id']").val();
        ajax.jsonRpc('/shop/cart/update_json', 'call', {
          product_id: Number(product_id),
          line_id: undefined,
          add_qty:1,
          set_qty: undefined,
          no_variant_attribute_values:"[]",
          product_custom_attribute_values:"[]",
        }).then(data =>{
            location.href = "/shop/cart";
        })
    },
    _sticky_buy_now:function(){
        this.$target.find(".o_we_buy_now").trigger("click");
    },
    _as_scroll_top:function (ev) {
        $("html, body").animate({ scrollTop: 0 }, "slow");
    },
    _product_rating:function(ev){
        this.$target.find("#nav_tabs_link_3").trigger("click");
    },
    _stickyCart:function(ev){
        var cr = this;
        var addToCartBtns = cr.$target.find('#add_to_cart');
        if(cr.$target.find('.as-sticky-cart-active').length != 0 && addToCartBtns.length != 0){
            const top = cr.$target.find('#add_to_cart').offset().top;
            const bottom = cr.$target.find('#add_to_cart').offset().top + cr.$target.find('#add_to_cart').outerHeight();
            const bottom_screen = $(window).scrollTop() + $(window).innerHeight();
            const top_screen = $(window).scrollTop();
            if ((bottom_screen > top) && (top_screen < bottom)){
                if(cr.$target.find('.as-product-sticky-cart').hasClass("as-stikcy-show")){
                    cr.$target.find('.as-product-sticky-cart').removeClass("as-stikcy-show");
                }
            } else {
                if(top < 0){
                    if(!cr.$target.find('.as-product-sticky-cart').hasClass("as-stikcy-show")){
                        cr.$target.find('.as-product-sticky-cart').addClass("as-stikcy-show");
                    }
                }
            }
        }
        var offset = 450;
        var $back_to_top = $('.as-scroll-to-top');
        ($('#wrapwrap').scrollTop() > offset) ? $back_to_top.addClass('as-bt-visible'): $back_to_top.removeClass('as-bt-visible');
    },
});

let AlanQuickView = Dialog.extend({
    events: _.extend({}, Dialog.prototype.events, { 'click .as_close': 'close' }),
    init: function (ele, otps) {
        this.product_id = otps.product_id;
        let dialog_props = {
                            backdrop: true,
                            size: 'extra-large',
                            technical: false,
                            renderHeader: false,
                            renderFooter: false,
                        };
        this._super(ele, _.extend(dialog_props, otps));
    },
    willStart: async function () {
        var template = ajax.jsonRpc('/get_quick_view', 'call', { product_id: this.product_id });
        return Promise.all([this._super(...arguments), template]).then((response) => {
            this.$content = $(response[1]);
            this.$modal.addClass("as-quick-view-modal");
        });
    },
    start: function () {
        $(this.$content).appendTo(this.$el);
        this.trigger_up('widgets_start_request', {
            $target: this.$content,
        });
        return this._super.apply(this, arguments);
    },
});

publicWidget.registry.alan_quick_view = publicWidget.Widget.extend({
    selector: ".as_quick_view",
    events:{
        'click':'_show_quick_view',
    },
    _show_quick_view:function(ev){
        this.AlanQuickView = new AlanQuickView(this, { product_id: parseInt($(ev.currentTarget).attr('data-product_tmpl_id')) });
        this.AlanQuickView.open();
    }
});

publicWidget.registry.as_shop_info = publicWidget.Widget.extend({
    selector:".o_wsale_products_page",
    events:{
        'click .as-clear-filter':'_clearFilter',
    },
    _clearFilter:function(ev){
        const fieldName = $(ev.currentTarget).data("name");
        const fieldValue = $(ev.currentTarget).data("value");
        const $filterForm = this.$target.find("form.js_attributes");
        const $input = $filterForm.find('input[name="'+fieldName+'"][value="' + fieldValue + '"]');
        if($input.length == 0){
            const $option = $filterForm.find('option[value=' + fieldValue + ']');
            $option.closest('select').val('').trigger("change");
        }
        $input.prop('checked', false);
        $input.trigger("change");
    },
    start: function () {
        new Swiper(".as_wsale_filmstip", {
            slidesPerView: "auto",
            spaceBetween: 10,
            navigation: {
              nextEl: ".swiper-button-next",
              prevEl: ".swiper-button-prev",
            },
        });
        return this._super.apply(this, arguments);
    },
});

const AlanSimilarProduct = Dialog.extend({
    events: _.extend({}, Dialog.prototype.events, { 'click .as_close': 'close' }),

    init: function (ele, otps) {
        this.product_id = otps.product_id;
        let dialog_props = {
                            backdrop: true,
                            size: 'extra-large',
                            technical: false,
                            renderHeader: false,
                            renderFooter: false,
                        };
        this._super(ele, _.extend(dialog_props , otps || {}));
    },

    willStart: async function () {
        var template = ajax.jsonRpc('/get_similar_product', 'call', { product_id: this.product_id });
        return Promise.all([this._super(...arguments), template]).then((response) => {
            this.$content = $(response[1]);
            this.$modal.addClass("as-similar-product-modal");
        });
    },

    start: function () {
        $(this.$content).appendTo(this.$el);
        return this._super.apply(this, arguments);
    },
});

publicWidget.registry.alan_similar_product = publicWidget.Widget.extend({
    selector: ".as_similar_product",
    events:{
        'click':'_show_similar_product',
    },
    _show_similar_product:function(ev){
        this.AlanSimilarProduct = new AlanSimilarProduct(this, { product_id: parseInt($(ev.currentTarget).attr('data-product_tmpl_id')) });
        this.AlanSimilarProduct.open();
    }
});

publicWidget.registry.ProductWishlist.include({
    selector: '#wrapwrap',
})
publicWidget.registry.ProductComparison.include({
    selector: '#wrapwrap',
})

publicWidget.registry.alan_website = publicWidget.Widget.extend(cartHandlerMixin, VariantMixin, {
    selector: "#wrapwrap",
    events:{
        'click #as_add_to_cart':'async _addToCart',
    },
    _addToCart:function(ev){
        ev.preventDefault();
        var def = () => {
            this.isBuyNow = ev.currentTarget.classList.contains('o_we_buy_now');
            const targetSelector = ev.currentTarget.dataset.animationSelector || 'img';
            this.$itemImgContainer = this.$(ev.currentTarget).closest(`:has(${targetSelector})`);
            return this._handleAdd($(ev.currentTarget).closest('form'));
        };
        return def();
    },
    _handleAdd: function ($form) {
        var self = this;
        this.$form = $form;
        var productSelector = [
            'input[type="hidden"][name="product_id"]',
            'input[type="radio"][name="product_id"]:checked'
        ];
        var productReady = this.selectOrCreateProduct(
            $form,
            parseInt($form.find(productSelector.join(', ')).first().val(), 10),
            $form.find('.product_template_id').val(),
            false
        );
        return productReady.then(function (productId) {
            $form.find(productSelector.join(', ')).val(productId);
            self._updateRootProduct($form, productId);
            return self._onProductReady();
        });
    },
    _updateRootProduct($form, productId) {
        this.rootProduct = {
            product_id: productId,
            quantity: parseFloat($form.find('input[name="add_qty"]').val() || 1),
            product_custom_attribute_values: this.getCustomVariantValues($form.find('.js_product')),
            variant_values: this.getSelectedVariantValues($form.find('.js_product')),
            no_variant_attribute_values: this.getNoVariantAttributeValues($form.find('.js_product'))
        };
    },
    _onProductReady: function () {
        return this._submitForm();
    },
    _submitForm: function () {
        const params = this.rootProduct;
        params.add_qty = params.quantity;
        params.product_custom_attribute_values = JSON.stringify(params.product_custom_attribute_values);
        params.no_variant_attribute_values = JSON.stringify(params.no_variant_attribute_values);
        delete params.quantity;
        this.stayOnPageOption = true;
        return this.addToCart(params);
    },

});

searchBar.include({
    xmlDependencies:['/theme_alan/static/src/xml/mixins/search_bar.xml', '/website/static/src/snippets/s_searchbar/000.xml'],
    _render: function (res) {
        const $prevMenu = this.$menu;
        this.$el.toggleClass('dropdown show', !!res);
        if (res && this.limit) {
            const results = res['results'];
            if (this.searchType == 'as_advance_search') {
                var template = 'theme_alan.s_alan_searchbar';
            }else{
                var template = 'website.s_searchbar.autocomplete';
            }
            const candidate = template + '.' + this.searchType;
            if (qweb.has_template(candidate)) {
                template = candidate;
            }
            this.$menu = $(qweb.render(template, {
                results: results,
                brands: res['brands'],
                tags: res['tags'],
                category: res['category'],
                products: res['products'],
                parts: res['parts'],
                hasMoreResults: results.length < res['results_count'],
                search: this.$input.val(),
                fuzzySearch: res['fuzzy_search'],
                widget: this,
            }));
            this.$menu.css('min-width', this.autocompleteMinWidth);
            this.$el.append(this.$menu);
            this.$el.find('button.extra_link').on('click', function (event) {
                event.preventDefault();
                window.location.href = event.currentTarget.dataset['target'];
            });
            this.$el.find('.s_searchbar_fuzzy_submit').on('click', (event) => {
                event.preventDefault();
                this.$input.val(res['fuzzy_search']);
                const form = this.$('.o_search_order_by').parents('form');
                form.submit();
            });
        }
        if ($prevMenu) {
            $prevMenu.remove();
        }
    },
    async _fetch() {
        if(this.searchType == "as_advance_search"){
            const res = await this._rpc({
                route: '/website/snippet/autocomplete',
                params: {
                    'search_type': this.searchType,
                    'term': this.$input.val(),
                    'order': this.order,
                    'limit': this.limit,
                    'max_nb_chars': Math.round(Math.max(this.autocompleteMinWidth, parseInt(this.$el.width())) * 0.22),
                    'options': this.options,
                },
            });
            const fieldNames = [
                'name',
                'description',
                'extra_link',
                'detail',
                'detail_strike',
                'detail_extra',
            ];
            if(res.products == undefined){
                res.products = [];
            }
            if(res.brands == undefined){
                res.brands = [];
            }
            if(res.tags == undefined){
                res.tags = [];
            }
            if(res.category == undefined){
                res.category = [];
            }
            const as_srch_lst = [res.products, res.brands, res.tags, res.category];
            as_srch_lst.forEach(ele => {
                ele.forEach(record => {
                    for (const fieldName of fieldNames) {
                        if (record[fieldName]) {
                            if (typeof record[fieldName] === "object") {
                                for (const fieldKey of Object.keys(record[fieldName])) {
                                    record[fieldName][fieldKey] = Markup(record[fieldName][fieldKey]);
                                }
                            } else {
                                record[fieldName] = Markup(record[fieldName]);
                            }
                        }
                    }
                });
            });
            return res;
        }
        else{
            return this._super.apply(this, arguments);
        }

    },
})

publicWidget.registry.MegaMenuTabsSnippets = publicWidget.Widget.extend({
    selector: '.as-mm-tabs-level-1',
    disabledInEditableMode:false,
    events:{
        'mouseenter':'_showMegaMenuTabs',
        'click .as-mob-tab-menu':'_showMegaMenuTabsMob',
    },
    _showMegaMenuTabs:function(ev){
        if($(ev.currentTarget).hasClass("active") == false){
            this.$target.parents(".as-mm-tabs-levels").find(".as-mm-tabs-level-1.active").removeClass("active");
            $(ev.currentTarget).addClass("active");
        }
    },
    _showMegaMenuTabsMob:function(ev){
        ev.preventDefault();
        ev.stopPropagation();
        if($(ev.currentTarget).parents(".as-mm-tabs-level-1").hasClass("as-mob-menu")){
            $(ev.currentTarget).parents(".as-mm-tabs-level-1").removeClass("active").removeClass("as-mob-menu");
        }else{
            $(ev.currentTarget).parents(".as-mm-tabs-level-1").addClass("active").addClass("as-mob-menu");
        }
    }
});

publicWidget.registry.MegaMenuSnippets = publicWidget.Widget.extend({
    selector: '.nav-item',
    disabledInEditableMode:false,
    is_clicked :false,
    events:{
        'click':'_showMegaMenu',
        'mouseenter':'_showMegaMenu',
    },
    _showMegaMenu: async function(ev){
        if(!this.is_clicked && !this.editableMode){
            let loader = '<div class="spinner-border" role="status"> <span class="visually-hidden">Loading...</span></div>'
            let snippetList = this.$target.find('[data-snippet-name]:not([data-snippet-name="MegaMenuContent"])').empty().append(loader);
            for (const snippet of snippetList) {
                let static_snippet = ['MegaMenuContent'];
                if(!static_snippet.includes($(snippet).attr("data-snippet-name"))){
                    let context = {
                        'snippet':$(snippet).attr("data-snippet-name"),
                        'record_ids':JSON.parse($(snippet).attr("data-records-ids")),
                        'modal':$(snippet).attr("data-modal"),
                        'design_editor':JSON.parse($(snippet).attr("data-design-edit")),
                    }
                    if($(snippet).attr("data-snippet-name") == "MegaMenuCategory"){
                        context['extra_info'] = JSON.parse($(snippet).attr("data-extra-info"))
                    }
                    let response = await this._rpc({
                        route:"/get_mega_snippet_template",
                        params: context
                    });
                    var $template =  $(response['template']).attr("id","as_swiper_slider_as");

                    $(snippet).empty().append($template);
                    if(Object.keys(response.slider_config).length != 0){
                        new Swiper("#as_swiper_slider_as", response.slider_config);
                    }
                    $template.removeAttr("id");
                }
            }
            this.is_clicked = true;
        }
    }
})

let AlanSliders = publicWidget.Widget.extend({
    _getProductSlider:function(){
        for (const product_slider of this.$target) {
            let context = {
                'snippet':$(product_slider).attr("data-snippet-name"),
                'record_ids':JSON.parse($(product_slider).attr("data-records-ids")),
                'modal':$(product_slider).attr("data-modal"),
                'design_editor':JSON.parse($(product_slider).attr("data-design-edit")),
            }
            if(!this.editableMode){
                this._rpc({
                    'route':'/get_products_snippet_template',
                    'params':context
                }).then((res)=>{
                    if(this.selector == "[data-snippet-name='CategoryProduct']" || this.selector == "[data-snippet-name='BrandProduct']"){
                        $(product_slider).empty().append(res['template']);
                        var $template = $(product_slider).find('.as_page_swiper')
                        for (let s_templ of $template) {
                            $(s_templ).attr("id",'as_swiper_slider_as');
                            if(Object.keys(res.slider_config).length != 0){
                                new Swiper("#as_swiper_slider_as", res.slider_config);
                            }
                            $(s_templ).removeAttr("id","as_swiper_slider_as")
                        }

                    }else{

                        if('record_ids' in res){
                            $(product_slider).attr("data-records-ids", JSON.stringify(res.record_ids))
                        }
                        var $template =  $(res['template']).attr("id","as_swiper_slider_as");
                        $(product_slider).empty().append($template);
                        if(Object.keys(res.slider_config).length != 0){
                            new Swiper("#as_swiper_slider_as", res.slider_config);
                        }
                        $template.removeAttr("id");
                    }
                    this.trigger_up('widgets_start_request', {$target: $template});
                    this.trigger_up('widgets_start_request', {$target: $(".as_quick_view")});
                    this.trigger_up('widgets_start_request', {$target: $(".as_color_variant")});
                });
            }else{
                $(product_slider).parents(".s_dynamic_snippets").attr("contenteditable",true)
                $(product_slider).empty().append("<div class='text-center'> <h3>"+$(product_slider).attr("data-snippet-name")+"</h3> </div>");
            }
        }
    },
    _tab_change:function(ev){
        this.$target.find(".as-tab-name").removeClass("active");
        let tab_id = $(ev.currentTarget).data('id');
        $(ev.currentTarget).addClass('active');
        if(this.selector == "[data-snippet-name='CategoryProduct']"){
            var slider_tab = "[data-tab-id='category_"+tab_id+"']";
            this.$target.find(".as_category_products").removeClass("active");

        }else{
            var slider_tab = "[data-tab-id='brand_"+tab_id+"']";
            this.$target.find(".as_brand_products").removeClass("active");
        }
        this.$target.find(".as-tab-pane").removeClass("active")
        this.$target.find(slider_tab).addClass("active");
    },
    _get_loader:function(){
        var loader = '<div class="card">\
            <svg class="bd-placeholder-img card-img-top" width="100%" height="180" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Placeholder" preserveAspectRatio="xMidYMid slice" focusable="false">\
                <title>Placeholder</title>\
                <rect width="100%" height="100%" fill="#868e96"></rect>\
            </svg>\
            <div class="card-body">\
                <h5 class="card-title placeholder-glow">\
                    <span class="placeholder col-6"></span>\
                </h5>\
                <p class="card-text placeholder-glow">\
                    <span class="placeholder col-7"></span>\
                    <span class="placeholder col-4"></span>\
                    <span class="placeholder col-4"></span>\
                    <span class="placeholder col-6"></span>\
                    <span class="placeholder col-8"></span>\
                </p>\
                <a href="#" tabindex="-1" class="btn btn-primary disabled placeholder col-6"></a>\
            </div>\
        </div>';
        this.$target.empty().append(loader)
    }
});


publicWidget.registry.alanProductSlider = AlanSliders.extend({
    selector:"[data-snippet-name='ProductSlider']",
    disabledInEditableMode: false,
    start:function(){
        this._get_loader()
        this._getProductSlider();
    }
});


publicWidget.registry.alanBestSellingProduct = AlanSliders.extend({
    selector:"[data-snippet-name='BestSellingProduct']",
    disabledInEditableMode: false,
    start:function(){
        this._get_loader()
        this._getProductSlider();
    }
});

publicWidget.registry.alanLatestProduct = AlanSliders.extend({
    selector:"[data-snippet-name='LatestProduct']",
    disabledInEditableMode: false,
    start:function(){
        this._get_loader()
        this._getProductSlider();
    }
});

publicWidget.registry.alanCategoryProduct = AlanSliders.extend({
    selector:"[data-snippet-name='CategoryProduct']",
    disabledInEditableMode: false,
    events:{
        'click .as-tab-name':'_tab_change'
    },
    start:function(){
        this._get_loader()
        this._getProductSlider();
    }
});

publicWidget.registry.alanBrandProduct = AlanSliders.extend({
    selector:"[data-snippet-name='BrandProduct']",
    disabledInEditableMode: false,
    events:{
        'click .as-tab-name':'_tab_change'
    },
    start:function(){
        this._get_loader()
        this._getProductSlider();
    }
});


publicWidget.registry.alanProductBanner = AlanSliders.extend({
    selector:"[data-snippet-name='ProductBanner']",
    disabledInEditableMode: false,
    start:function(){
        this._get_loader()
        this._getProductSlider();
    }
});


publicWidget.registry.alanCategorySlider = AlanSliders.extend({
    selector:"[data-snippet-name='CategorySlider']",
    disabledInEditableMode: false,
    start:function(){
        this._get_loader()
        this._getProductSlider();
    }
});

publicWidget.registry.alanBrandSlider = AlanSliders.extend({
    selector:"[data-snippet-name='BrandSlider']",
    disabledInEditableMode: false,
    start:function(){
        this._get_loader()
        this._getProductSlider();
    }
});

publicWidget.registry.alanBlogSlider = AlanSliders.extend({
    selector:"[data-snippet-name='BlogSlider']",
    disabledInEditableMode: false,
    start:function(){
        this._get_loader()
        this._getProductSlider();
    }
});

var prod_fetch_call = false;

publicWidget.registry.alanAjaxProductLoad = publicWidget.Widget.extend({
    selector:".as_shop_page",
    events:{
        'click .as_ajax_product_load':'_loadProduct'
    },
    _loadProduct:function(){
        let products = localStorage.getItem("as_next_product_set");
        let pager = localStorage.getItem("as_next_pager_set");
        let $product_tbody = this.$target.find(".o_wsale_products_grid_table_wrapper").find("tbody");
        let $product_pager =  this.$target.find(".products_pager");
        if(products != undefined && pager != undefined){
            $product_tbody.append(products);
            $($product_pager).empty().append(pager);
        }
        let next_url = $(".products_pager").find("li.active").next().find("a").attr("href");
        if(next_url != undefined && next_url != ""){
            $.ajax({
                url: next_url,
                type: 'GET',
                success: function (response) {
                    var products = $(response).find(".o_wsale_products_grid_table_wrapper").find("tbody").html();
                    var pager = $(response).find(".products_pager").html();
                    localStorage.setItem("as_next_product_set", products)
                    localStorage.setItem("as_next_pager_set", pager)
             }})
        }else{
            localStorage.removeItem("as_next_product_set")
            localStorage.removeItem("as_next_pager_set")
        }
        this.trigger_up('widgets_start_request', {
            $target: $('.as_similar_product'),
        });
        this.trigger_up('widgets_start_request', {
            $target: $('.as_quick_view'),
        });
        this.trigger_up('widgets_start_request', {
            $target: $('.as_color_variant'),
        });
        this.trigger_up('widgets_start_request', {
            $target: $('.as_offer_timer'),
        });

    },
    start:function(){
        this.$target.on('scroll', _.throttle((ev) => {
            if(this.$target.find('.as_ajax_product_load').offset() != undefined){
                var gettop = this.$target.find('.as_ajax_product_load').offset().top;
                var getheight = this.$target.find('.as_ajax_product_load').outerHeight();
                var getwindowheight = $(window).height();
                var nxtbtnpos = gettop+getheight-getwindowheight;
                if (nxtbtnpos < 30){
                    if(prod_fetch_call != true){
                        this._loadProduct()
                        prod_fetch_call = true;
                    }
                }else{
                    prod_fetch_call = false;
                }
            }
        }, 15));

        let next_url = this.$target.find(".products_pager").find("li.active").next().find("a").attr("href");
        if(next_url != undefined && next_url != ""){
            $.ajax({
                url: next_url,
                type: 'GET',
                success: function (response) {
                    var products = $(response).find(".o_wsale_products_grid_table_wrapper").find("tbody").html();
                    var pager = $(response).find(".products_pager").html();
                    localStorage.setItem("as_next_product_set", products);
                    localStorage.setItem("as_next_pager_set", pager);
             }})
        }else{
            localStorage.removeItem("as_next_product_set");
            localStorage.removeItem("as_next_pager_set");
        }
    }
});

publicWidget.registry.alanAttributeSearch = publicWidget.Widget.extend({
    selector:'.as_attr_search',
    events:{
        'keyup':'_search_attribute'
    },
    _search_attribute(){
        let curr_val = this.$target.val().toLowerCase();
        for (const iter of this.$target.parents(".accordion-body").find(".as_attr")) {
            let attr = $(iter).data('name').toLowerCase();
            if(!attr.includes(curr_val)){
                $(iter).addClass("d-none")
            }else{
                $(iter).removeClass("d-none")
            }
        }
    }
})

publicWidget.registry.alanImageHotSpots = publicWidget.Widget.extend({
    selector:'.hotspot',
    start:function(ev){
        if(this.$target.find(".hs_icon").hasClass("dynamic_type")){
            if(this.$target.find(".hs_icon").attr("data-dy_type") == "popover"){
                let prod_tmpl_id = this.$target.find(".hs_icon").attr("data-product_tmpl_id");
                var pop_style = this.$target.find(".hs_icon").attr('data-po_style') == undefined ? '' :this.$target.find(".hs_icon").attr('data-po_style');
                this._rpc({
                    route: '/get_hotspot_product',
                    params: {'product_tmpl_id':prod_tmpl_id, 'style':pop_style}
                }).then((res) => {
                    this._showPopover(res['template']);
                });
            }
            else if(this.$target.find(".hs_icon").attr("data-dy_type") == "modal"){
                this.$target.find(".hs_icon").addClass("as_quick_view");
                this.trigger_up('widgets_start_request', {
                    $target: $('.as_quick_view'),
                });
            }
        }else if(this.$target.find(".hs_icon").hasClass("static_type")){
            var title = this.$target.find(".hs_icon").attr('data-po_title') == undefined ? '':this.$target.find(".hs_icon").attr('data-po_title');
            var description = this.$target.find(".hs_icon").attr('data-po_desc') == undefined ? '':this.$target.find(".hs_icon").attr('data-po_desc');
            var btn_txt = this.$target.find(".hs_icon").attr('data-po_btxt') == undefined ? '':this.$target.find(".hs_icon").attr('data-po_btxt');

            var language = document.getElementsByTagName("html")[0].getAttribute("lang");
            var activeLang = language.replace(/-/g, "_");

            var data_lang = 'data-lang-'
            var activeLanguage = data_lang.concat("",activeLang);
            if(this.$target.find(".hs_icon").attr(activeLanguage)){
                title = this.$target.find(".hs_icon").attr(activeLanguage) == undefined ? '':this.$target.find(".hs_icon").attr(activeLanguage);
            }

            var data_descr_lang = 'data-description-lang-'
            var activeLanguageDescription = data_descr_lang.concat("",activeLang);
            if(this.$target.find(".hs_icon").attr(activeLanguageDescription)){
                description = this.$target.find(".hs_icon").attr(activeLanguageDescription) == undefined ? '':this.$target.find(".hs_icon").attr(activeLanguageDescription);
            }

            var data_btn_lang = 'data-btn-lang-'
            var activeLanguageBtn = data_btn_lang.concat("",activeLang);
            if(this.$target.find(".hs_icon").attr(activeLanguageBtn)){
                btn_txt = this.$target.find(".hs_icon").attr(activeLanguageBtn) == undefined ? '':this.$target.find(".hs_icon").attr(activeLanguageBtn);
            }

            var btn_url = this.$target.find(".hs_icon").attr('data-po_bturl') == undefined ? '':this.$target.find(".hs_icon").attr('data-po_bturl');
            var img_url = this.$target.find(".hs_icon").attr('data-po_imgurl') == undefined ? '' :this.$target.find(".hs_icon").attr('data-po_imgurl');
            var pop_thm = this.$target.find(".hs_icon").attr('data-po_theme') == undefined ? '' :this.$target.find(".hs_icon").attr('data-po_theme');
            var pop_style = this.$target.find(".hs_icon").attr('data-po_style') == undefined ? '' :this.$target.find(".hs_icon").attr('data-po_style');
            var context = { 'title':title,'description':description,'btn_txt':btn_txt,
                'btn_url':btn_url,'img_url':img_url,'pop_thm':pop_thm, 'pop_style':pop_style }
            if(this.$target.find(".hs_icon").attr("data-st_type") == "popover"){
                let template = qweb.render("theme_alan.s_static_hotspot_popover", {data:context})
                this._showPopover(template);
            }
            else if(this.$target.find(".hs_icon").attr("data-st_type") == "modal"){
                this.$target.find(".hs_icon").on("click",function(){
                    new Dialog(this, {
                        $content:$(qweb.render("theme_alan.s_static_hotspot_popover", {data:context})),
                        renderHeader: false,
                        renderFooter: false,
                        backdrop: true,
                    }).open();
                })
            }
        }
    },
    _showPopover(template){
        var self = this;
        this.$target.find(".hs_icon").popover({
            html: true,
            container: 'body',
            trigger : 'manual',
            content: $(template),
        }).on("mouseenter", function () {
            $(this).popover("show");
            $(".popover").on("mouseleave", function () {
                self.$target.find(".hs_icon").popover('hide');
            }).addClass("as-popover");
        }).on("mouseleave", function () {
            setTimeout(function () {
                if (!$(".popover:hover").length) {
                    self.$target.find(".hs_icon").popover('hide');
                }
            }, 100);
        });

    }
})

const ProductQueriesInfo = Dialog.extend({
    events:({
        'click .as_close': 'close',
        'click .send_questions': '_sendClick',
        'keyup textarea.msg': '_onChangeInput',
    }),
    init(ele, otps) {
        this.product_id = otps.product_id;
        this.user_id = otps.user_id;
        this.parent = ele
        this._super(ele, {
            backdrop: true,
            size: 'extra-large',
            technical: false,
            renderHeader: false,
            renderFooter: false,
        });
    },

    willStart: async function () {
        const res = this._super(...arguments);
        var self = this;
        return rpc.query({
            route: '/product_queries',
            params: { product_id: this.product_id }
        }).then(function (template) {
            if (template) {
                self.$content = $(template);
                self.opened().then(() => {
                    var $modal = $('.modal');
                    if ($modal.length) {
                        $modal.addClass("as-queries-modal");
                    }
                });
            }
            else{
                $('.query-msg')[0].classList.remove("d-none");
                self.close()
            }
        });
    },

    start: function () {
        return this._super.apply(this, arguments);
    },

    _sendClick: function(ev){
        var self = this
        var email = $("#email").val();
        var message = $("#message").val()
        var user_id = $("#customer_id").val()
        let radios = $('.ContactPreference');
        let selectedValue = '';
        for (let i = 0; i < radios.length; i++) {
            if (radios[i].checked) {
                selectedValue = radios[i].id;
                break;
            }
        }
        if (message == '') {
            $(".msg").addClass("border").addClass("border-danger")
        }
        var context = { message: message,user_id:user_id,email:email,product_id:this.product_id,contact_preference:selectedValue}
        if (message){
            return rpc.query({
                route: '/send_queries_mail',
                params: context
            }).then(function() {
                $(".dialog-container").hide();
                $("#thank-you").removeClass("o_hidden");
                setTimeout(function() {
                    self.close()
                  }, 2000);
            })
        }
    },

    _onChangeInput:function(){
        $(".msg").removeClass("border").removeClass("border-danger")
    },
})

publicWidget.registry.ProductQueries =publicWidget.Widget.extend({
    selector: '.product_queries',
    events : {
        'click #any_queries': '_onClickQueries',
    },

    _onClickQueries:function(){
        let inputproduct = $("#product").val();
        let inputuser = $("#user").val();
        new ProductQueriesInfo(this,{ product_id: inputproduct,user_id:inputuser}).open();

    }
});

export default {
    searchBar: searchBar,
}