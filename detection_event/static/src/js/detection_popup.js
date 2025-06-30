odoo.define('detection_event.popup', function (require) {
    "use strict";

    var bus = require('web.bus');
    var Dialog = require('web.Dialog');

    bus.on('new_detection_event', null, function(event_data) {
        Dialog.alert(null, "Hello World!", {
            title: "Yeni Algılama Olayı: " + event_data.name,
            size: 'medium',
        });
    });
});