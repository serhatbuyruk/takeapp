// static/src/js/auto_refresh.js
odoo.define('detection_event.auto_refresh', function (require) {
    "use strict";

    const ListController = require('web.ListController');
    const viewRegistry = require('web.view_registry');
    const ListView = require('web.ListView');

    const AutoRefreshListController = ListController.extend({
        start: function () {
            this._super.apply(this, arguments);
            
            // Sadece detection_event.profile modelinde otomatik yenileme
            if (this.modelName === 'detection_event.profile') {
                this._startAutoRefresh();
            }
            
            return Promise.resolve();
        },

        _startAutoRefresh: function () {
            console.log('Auto refresh başlatıldı - 15 saniye aralık');
            this._refreshInterval = setInterval(() => {
                console.log('Liste yenileniyor...');
                this.update({}, { reload: true });
            }, 15000); // 15 saniye
        },

        destroy: function () {
            if (this._refreshInterval) {
                clearInterval(this._refreshInterval);
                console.log('Auto refresh durduruldu');
            }
            this._super.apply(this, arguments);
        },
    });

    const AutoRefreshListView = ListView.extend({
        config: _.extend({}, ListView.prototype.config, {
            Controller: AutoRefreshListController,
        }),
    });

    // View registry'ye ekle
    viewRegistry.add('auto_refresh_list', AutoRefreshListView);

    console.log('Auto refresh modülü yüklendi');
});