/** @odoo-module **/

import { registerPatch } from '@mail/model/model_core';
import { attr } from '@mail/model/model_field';


registerPatch({
    name: 'Message',
    modelMethods: {
        /**
         * @override
         */
        convertData(data) {
            const data2 = this._super(data);
            if ('new_tab' in data) {
                data2.newTab = data.new_tab;
            }
            if ('show_popup' in data) {
                data2.showPopup = data.show_popup;
            }
            return data2;
        },
    },
    fields: {
        newTab: attr({
            default: false,
        }),
        showPopup: attr({
            default: false,
        }),
    },
});
