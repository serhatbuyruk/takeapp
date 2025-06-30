/** static/src/js/auto_refresh_list.js **/
odoo.define('detection_event.auto_refresh_list', function (require) {
    "use strict";
    const ListController = require('web.ListController');
    const viewRegistry = require('web.view_registry');

    const AutoRefreshListController = ListController.extend({
        /**
         * start() ömrü başladığında devreye girer.
         * Sadece detection_event.profile modelinin list görünümünde
         * çalışacak şekilde, her 15 sn’de bir reload() çağırıyoruz.
         */
        start: function () {
            const res = this._super.apply(this, arguments);
            if (this.modelName === 'detection_event.profile') {
                this._refreshInterval = setInterval(() => {
                    this.reload();
                }, 15000);
            }
            return res;
        },
        /**
         * Controller yok edilirken (örneğin form view’e geçince)
         * interval’i temizliyoruz.
         */
        destroy: function () {
            if (this._refreshInterval) {
                clearInterval(this._refreshInterval);
            }
            return this._super.apply(this, arguments);
        },
    });

    viewRegistry.add('auto_refresh_list', AutoRefreshListController);
});
