odoo.define('detection_event.CustomPopup2', function (require) {
    "use strict";

    const core = require('web.core');
    const Dialog = require('web.Dialog');
    const AbstractAction = require('web.AbstractAction');

    const CustomPopupAction = AbstractAction.extend({
        init: function(parent, action) {
            this._super.apply(this, arguments);
            this.data = action.params || {};
        },
        
        start: function() {
            const $content = $(core.qweb.render('custom_popup_template2', {
                widget: { data: this.data }
            }));
            
            this.dialog = new Dialog(this, {
                title: "Olay Detayları",
                size: 'medium',
                $content: $content,
                buttons: [
                    {
                        text: "Kapat",
                        close: true,
                        class: 'btn-primary',
                    }
                ],
            }).open();

            return this._super.apply(this, arguments);
        },
    });

    core.action_registry.add('custom_popup_action', CustomPopupAction);
});