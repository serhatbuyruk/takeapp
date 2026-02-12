/** @odoo-module **/

import { SnippetBuilderWrapper } from 'theme_alan.SnippetBuilder';
import { ComponentWrapper } from 'web.OwlCompatibility';
import { registry } from "@web/core/registry";
import { _t } from "web.core";
import options from 'web_editor.snippets.options';
import {SnippetsMenu} from "web_editor.snippet.editor"

SnippetsMenu.include({
    _onSaveRequest: function (ev) {
        let static_snippet_list = ['MegaMenuContent', 'StaticSnippet'];
        let $snippet_list = this.$body.find(".as-grid");
        for (let snippet of $snippet_list) {
           if(!static_snippet_list.includes($(snippet).attr("data-snippet-name"))){
                $(snippet).empty();
           }
        }
        this._super.apply(this, arguments);
    }
})

options.registry.as_snippet_configure = options.Class.extend({
    xmlDependencies: ["/theme_alan/static/src/xml/mixins/template.xml"],
    start:function(){
        /** Call configuration method on first time and on click */
        this._super.apply(this, arguments);
        this._openSnippetConfigure();
        this.$target.click(() => {this._openSnippetConfigure()});
    },
    _openSnippetConfigure: function (ev) {
        /** Fetch snippet detail and open configure dialog */
        if (!this.snippetProcessing) {
            var snippet_type = this.$target.attr("data-as-snippet");
            if (snippet_type == undefined) {
                if (this.$target.hasClass("as_mega_menu")) {
                    snippet_type = "as_mega_menu";
                }
            }
            const snippet_list = registry.category("as_snippet_registry").get(snippet_type);
            const is_static = this.$target.hasClass("as_static_menu");
            if (!is_static) {
                if (snippet_type == "as_mega_menu") {
                    let data = { 'title': 'Megamenu Configuration', 'snippet_list': snippet_list, 'snippet_origin': this }
                    let dialog = new ComponentWrapper(this, SnippetBuilderWrapper, data);
                    dialog.mount(this.el);
                } else if (snippet_type == "as_dynamic_snippets") {
                    let data = { 'title': 'Alan Snippet Configuration', 'snippet_list': snippet_list, 'snippet_origin': this }
                    let dialog = new ComponentWrapper(this, SnippetBuilderWrapper, data);
                    dialog.mount(this.el);
                }
            }
        }
    },
});
