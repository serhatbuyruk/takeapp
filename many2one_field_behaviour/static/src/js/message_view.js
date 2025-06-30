/* @odoo-module */

import { registerPatch } from '@mail/model/model_core';
import { Many2XAutocomplete, useOpenMany2XRecord } from "@web/views/fields/relational_utils";


registerPatch({
    name: 'MessageView',
    recordMethods: {

        async onClick(ev) {
            if (ev.target.tagName === 'A') {
                const model = ev.target.dataset.oeModel;
                const id = Number(ev.target.dataset.oeId);

                if (this.message.newTab) {
                    var href = '#id=' + id + '&model=' + model;
                    var newWindow = window.open(href, '_blank');
                    if (newWindow) {
                        newWindow.document.location = href;
                    }
                }
                else if (this.message.showPopup) {
                    const title = 'Open: ' + ev.target.text.trim();

                    this.env.services.action.doAction({
                        name: title,
                        type: 'ir.actions.act_window',
                        res_model: model,
                        views: [[false, 'form']],
                        res_id: id,
                        target: 'new',
                        context: { create: false, edit: false },
                    });

                }
                else {
                    this._super(...arguments);
                }
            }
            else {
                this._super(...arguments);
            }
        },
    },
});

