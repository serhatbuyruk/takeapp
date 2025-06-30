/** @odoo-module */
import { FormController } from "@web/views/form/form_controller";
import { patch } from "@web/core/utils/patch";
import { useService } from "@web/core/utils/hooks";
import { useSetupView } from "@web/views/view_hook";
import { session } from "@web/session"; // import session object

patch(FormController.prototype, 'FormController', {
    /* Patch FormController to restrict auto save in form views */
    setup() {
        this._super();
        this.uiService = useService("ui");
        this.beforeLeaveHook = false;
        useSetupView({
            beforeLeave: () => this.beforeLeave(),
            beforeUnload: (ev) => this.beforeUnload(ev),
        });
    },
    async beforeLeave() {
        /* function will work before leaving the form */
        // Adding current user language and logging to console
        const currentUserLanguage = session.user_context.lang;
        var lang_status = "not_found"
        //console.log("Current user's language:", currentUserLanguage);
        if (this.model.root.isDirty && this.beforeLeaveHook == false && currentUserLanguage == "en_US") {
            lang_status = "found"
            if (confirm("Do you want to save changes before leaving?")) {
                this.model.root.save({ noReload: true, stayInEdition: true })
            } else {
                this.model.root.discard();
            }
            this.beforeLeaveHook = true;
        }
        else if (this.model.root.isDirty && this.beforeLeaveHook == false && currentUserLanguage == "tr_TR") {
            lang_status = "found"
            if (confirm("Sayfadan Çıkmadan Önce Değişiklikler Kaydedilsin Mi?")) {
                this.model.root.save({ noReload: true, stayInEdition: true })
            } else {
                this.model.root.discard();
            }
            this.beforeLeaveHook = true;
        }
        else if (this.model.root.isDirty && this.beforeLeaveHook == false && currentUserLanguage == "de_DE") {
            lang_status = "found"
            if (confirm("Änderungen vor Verlassen der Seite speichern?")) {
                this.model.root.save({ noReload: true, stayInEdition: true })
            } else {
                this.model.root.discard();
            }
            this.beforeLeaveHook = true;
        }
        else if (this.model.root.isDirty && this.beforeLeaveHook == false && currentUserLanguage == "ru_RU") {
            lang_status = "found"
            if (confirm("Сохранить изменения перед выходом со страницы?")) {
                this.model.root.save({ noReload: true, stayInEdition: true })
            } else {
                this.model.root.discard();
            }
            this.beforeLeaveHook = true;
        }
        else if (this.model.root.isDirty && this.beforeLeaveHook == false && lang_status == "not_found") {
            if (confirm("Do you want to save changes before leaving?")) {
                this.model.root.save({ noReload: true, stayInEdition: true })
            } else {
                this.model.root.discard();
            }
            this.beforeLeaveHook = true;
        }
    },
    beforeUnload: async (ev) => {
        ev.preventDefault();
    }
});

