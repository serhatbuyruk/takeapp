// static/src/js/popup.js
odoo.define('detection_event.CustomPopup', function (require) {
    "use strict";

    const core = require('web.core');
    const Dialog = require('web.Dialog');

    function showCustomPopup() {
        Dialog.alert(this, {
            title: "Özel Popup",
            body: "Bu JavaScript ile oluşturulmuş bir popup!",
            buttons: [
                {
                    text: "Tamam",
                    classes: 'btn-primary',
                    close: true,
                }
            ],
        });
    }

    core.action_registry.add('show_custom_popup', showCustomPopup);
    return { showCustomPopup };
});