/** @odoo-module **/

import { ListController } from "@web/views/list/list_controller";
import core from "web.core";
var _t = core._t;
import { patch } from "@web/core/utils/patch";
const rpc = require("web.rpc");
const session = require("web.session");

var show_expand_collapse = false
rpc.query({
    model: 'res.users',
    method: 'search_read',
    fields: ['sh_enable_expand_collapse'],
    domain: [['id', '=', session.uid]]
}, { async: false }).then(function (data) {
    if (data) {
        _.each(data, function (user) {
            if (user.sh_enable_expand_collapse) {
                show_expand_collapse = true
            }
        });

    }
});

patch(ListController.prototype, 'sh_backmate_theme/static/src/js/list_controller.js', {
   
    setup(...args) {

        this._super(...args)
        this.show_expand_collapse = show_expand_collapse;    
    },

    _onClickRefreshView (ev) { 
        this.actionService.switchView('list');
    },

    shExpandGroups () {

        $(document).find('.o_group_header').each(function () {
            var $header = $(this);
            if (!$header.hasClass('o_group_open')) {
                $header.find('.o_group_name').click();
            }
        });
    },

    shCollapseGroups () {
        $(document).find('.o_group_header').each(function () {
            var $header = $(this);
            if ($header.hasClass('o_group_open')) {
                $header.find('.o_group_name').click();
            }
        });
    },
  
});

// odoo.define('sh_backmate_theme.ListController', function (require) {
//     "use strict";

//     var ListController = require('web.ListController');
//     var FormRenderer = require('web.FormRenderer');

//     FormRenderer.include({

        

//         _renderStatusbarButtons: function (buttons) {
//             var $statusbarButtons = $('<div>', {class: 'o_statusbar_buttons'});
//             buttons.forEach(button => $statusbarButtons.append(button));
//             var show_status_bar = false
//             _.each(buttons , function (button) {
//                     console.log(">>>>>>>>..",button.hasClass('o_invisible_modifier'))
//                 if(!button.hasClass('o_invisible_modifier')){
//                     show_status_bar = true
//                 }

//             });
            
//             if(!show_status_bar){
//                console.log(">>>>>>>>>>>.",$('.o_form_statusbar'))
//                console.log("999999",$statusbarButtons)
//                $statusbarButtons.remove()
//             }
//             return $statusbarButtons;
//         },
//     });


//     var ListRenderer = require('web.ListRenderer');

// 	ListRenderer.include({
// 		async _renderView() {
// 			// Fix issue of sticky three dots
// 			var self = this;
// 			return this._super.apply(this, arguments).then(function () {
// 				self.$el.find('thead').append(
// 								$('<i class="o_optional_columns_dropdown_toggle fa fa-ellipsis-v"/>')
// 							);
// 			});


// 		}
		    
// 	});

    
// });
