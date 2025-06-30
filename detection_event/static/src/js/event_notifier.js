console.log("event_notifier2 geldi")
odoo.define('detection_event.event_notifier', function (require) {
    "use strict";
    console.log("🚀 event_notifier.js yüklendi ve çalışıyor!");

    var core       = require('web.core');
    var QWeb       = core.qweb;
    var BusService = require('bus.BusService');
    var bus        = BusService;

    bus.addChannel('detection.event');
    bus.startPolling();
    bus.on('notification', null, function (notifications) {
        console.log("🔔 notification event geldi:", notifications);
        notifications.forEach(function (notif) {
            var channel = notif[1], data = notif[2];
            if (channel === 'detection.event') { _showPopup(data); }
        });
    });
    function _showPopup(data) {
        var $modal = $(QWeb.render('DetectionEventPopup', {widget: {data: data}}));
        $('body').append($modal);
        var bsModal = new bootstrap.Modal($modal);
        bsModal.show();
        $modal.on('hidden.bs.modal', function () { $modal.remove(); });
        $modal.find('.btn-submit').on('click', function () {
            require('web.rpc').query({
                model: 'detection_event.profile',
                method: 'action_acknowledge',
                args: [[data.id], $modal.find('#comments').val()],
            }).then(function () { bsModal.hide(); });
        });
    }
});

