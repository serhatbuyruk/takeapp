/** @odoo-module */

import { SearchModel } from "@web/search/search_model";
import { patch } from "@web/core/utils/patch";

patch(SearchModel.prototype, "tree_view_advanced_filter.SearchModel", {
    async _reloadSections() {
        this._super(...arguments);
        if (this.ak_domains) {
            this._domain = this.domain.concat(this.ak_domains);
        }
    },
});
