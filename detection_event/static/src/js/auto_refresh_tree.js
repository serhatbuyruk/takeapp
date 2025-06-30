/** @odoo-module **/

import { ListController } from "@web/views/list/list_controller";
import { patch } from "@web/core/utils/patch";

patch(ListController.prototype, "detection_event_auto_refresh", {
    setup() {
        this._super(...arguments);
        this.autoRefreshInterval = null;
    },

    async willStart() {
        await this._super(...arguments);
        // Sadece detection_event.profile modeli için ve tree view'de çalışacak
        if (this.props.resModel === 'detection_event.profile' && 
            this.env.config.viewType === 'list') {
            this.startAutoRefresh();
        }
    },

    startAutoRefresh() {
        // Eğer zaten bir interval varsa temizle
        if (this.autoRefreshInterval) {
            clearInterval(this.autoRefreshInterval);
        }
        
        // 15 saniyede bir yenile
        this.autoRefreshInterval = setInterval(async () => {
            try {
                // Sadece şu anki view tree view ise yenile
                if (this.env.config.viewType === 'list' && 
                    this.props.resModel === 'detection_event.profile') {
                    await this.model.load();
                    this.render();
                }
            } catch (error) {
                console.error('Auto refresh error:', error);
            }
        }, 15000); // 15 saniye
    },

    stopAutoRefresh() {
        if (this.autoRefreshInterval) {
            clearInterval(this.autoRefreshInterval);
            this.autoRefreshInterval = null;
        }
    },

    willUnmount() {
        this.stopAutoRefresh();
        this._super(...arguments);
    },

    // View değiştiğinde interval'i durdur
    onViewSwitched() {
        this.stopAutoRefresh();
        this._super(...arguments);
    }
});