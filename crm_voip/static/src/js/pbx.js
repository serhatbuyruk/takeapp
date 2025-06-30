odoo.define('web.pbx_notify', function (require) {
    "use strict";

    require('bus.BusService');
    // var Bus = require('web.Bus');
    var session = require('web.session');
    var Widget = require('web.Widget');
    var SystrayMenu = require('web.SystrayMenu');
    var Dialog = require('web.Dialog');
    var core = require('web.core');
    var _t = core._t;
    var QWeb = core.qweb;


    var PbxNotify = Widget.extend({
        template: 'crm_voip.pbx_menu',
        events: {
            "click #show_last_call": function () {
                this.open_dialog();
            },
            "click #missing_call_link": function () {
                this.missing_calls();
            }
        },
        last_call: {},
        missing_count: 0,
        lost_book: 0,
        theAudio: null,
        init: function () {
            this._super.apply(this, arguments);


        },
        missing_calls: function () {
            return this.do_action({
                type: 'ir.actions.act_window',
                name: "Customer Call",
                res_model: "crm_voip.crm.customer.call",
                views: [[false, 'list'], [false, 'form']],
                target: 'main',
                context: {
                    'search_default_unanswered': true,
                },
            });
        },
        start: function () {
            self = this;
            // this.bus = new Bus(this);
            this.call('bus_service', 'addChannel', "pbx_" + session.partner_id);
            this.call('bus_service', 'addChannel', "unanswered");
            this.call('bus_service', 'startPolling');
            this.call('bus_service', 'onNotification', this, this._onNotification);
            self._setMissingBadge();
        },
        _onNotification: function (notifications) {
            self = this;
            console.log(notifications);
            if (notifications.length > 0) {
                for (var index = 0; index < notifications.length; ++index) {
                    if (notifications[index][1] && notifications[index][1].hasOwnProperty("customer_number")) {
                        self.last_call = notifications[index][1];
                        self.open_dialog();
                        self.$el.find("#show_last_call").show()
                    } else if (notifications[index][0] && notifications[index][0] === "unanswered") {
                        self._setMissingBadge();
                    }
                }
            }
        },
        _stopAudio: function () {
            if (this.theAudio) {
                clearInterval(this.theAudio)
            }

        },
        _setMissingBadge: function () {
            self = this;
            this._rpc({
                model: 'crm_voip.crm.customer.call',
                method: 'search_count',
                args: [[["unanswered", "=", true]]],
            })
                .then(function (data) {
                    if (data > 0) {
                        self.$el.find(".missing_call_item").removeClass("o_no_notification");
                        self.$el.find(".unanswered_count").text(data);
                        if (self.missing_count < data) {
                            // self.$el.parent().find("#myAudio").get(0).play();
                            // self._playAudio();
                        }
                    } else {
                        self.$el.find(".missing_call_item").addClass("o_no_notification");
                        self.$el.find(".unanswered_count").text("");
                        // self._stopAudio();
                    }
                    self.missing_count = data;
                });
        },

        _playAudio: function () {
            // this._stopAudio();
            // this.theAudio = setInterval(function () {
            //     self.$el.parent().find("#myAudio").get(0).play();
            // }, 1000 * 5 * 60)
        },

        open_create_customer: function () {
            return this.do_action({
                type: 'ir.actions.act_window',
                view_type: 'form',
                view_mode: 'form',
                res_model: 'crm_voip.crm.create_customer_wizard',
                views: [[false, 'form']],
                res_id: this.last_call.customer_id,
                context: {
                    call_id: this.last_call.call_id
                },
                target: 'new',
            });
        },
        open_customer: function () {
            return this.do_action({
                type: 'ir.actions.act_window',
                view_type: 'form',
                view_mode: 'form',
                res_model: 'crm_voip.crm.customer',
                views: [[false, 'form']],
                res_id: this.last_call.customer_id,
            });

        },
        open_dialog: function () {
            var content = QWeb.render("crm_voip.pbx_dialog", this.last_call);

            var buttons = [];

            if (this.last_call.customer_exist) {
                buttons.push({
                    text: _t("Open Customer Detail"),
                    classes: 'btn-info',
                    close: true,
                    click: this.open_customer.bind(this),
                });

            } else {
                buttons.push({
                    text: _t("Create Customer"),
                    classes: 'btn-success',
                    close: true,
                    click: this.open_create_customer.bind(this),
                })
            }


            buttons.push({
                text: _t("Cancel"),
                close: true,
            });

            return new Dialog(this, {
                size: 'medium',
                buttons: buttons,
                $content: $('<div>', {
                    html: content
                }),
                title: _t("Incoming Call")
            }).open();
        }
    });
    $.when(
        session.user_has_group('crm_voip.crm_voip_manager'),
        session.user_has_group('crm_voip.crm_voip_full_access')
    ).then(function (crm_voip_manager, crm_voip_full_access) {
        if (
            crm_voip_manager ||
            crm_voip_full_access
        ) {

            SystrayMenu.Items.push(PbxNotify);
        }
    });

    return PbxNotify;
});