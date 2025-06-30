/** @odoo-module **/

const { onMounted } = owl;
import { patch } from "@web/core/utils/patch";
import { Many2OneField } from "@web/views/fields/many2one/many2one_field";
import {ReferenceField} from "@web/views/fields/reference/reference_field";
import {Many2OneBarcodeField} from "@web/views/fields/many2one_barcode/many2one_barcode_field";
//import {Many2OneAvatarField} from "@web/views/fields/many2one_avatar/many2one_avatar_field";

import {SaleOrderLineProductField} from "@sale/js/sale_product_field";

patch(SaleOrderLineProductField.prototype, "many2one_field_behaviour.SaleOrderLineProductField", {
    onClick(ev) {
        if (this.props.newTab) {
            var href = '#id=' + this.resId + '&model=' + this.relation;
            var newWindow = window.open(href, '_blank');
            if (newWindow) {
                newWindow.document.location = href;
            }
        }
        else if (this.props.showPopup) {
            this.openDialog(this.resId);
        }
        else {
            this._super(...arguments);
        }
    },
});

patch(Many2OneField.prototype, "many2one_field_behaviour.Many2OneField", {

    setup() {
        this._super(...arguments);
        this.focusInput = () => {
            if (this.autocompleteContainerRef.el !== undefined) {
                this.autocompleteContainerRef.el.querySelector("input").focus();
            }
        };
    },

    onClick(ev) {
        if (this.props.newTab) {
            var href = '#id=' + this.resId + '&model=' + this.relation;
            var newWindow = window.open(href, '_blank');
            if (newWindow) {
                newWindow.document.location = href;
            }
        }
        else if (this.props.showPopup) {
            this.openDialog(this.resId);
        }
        else {
            this._super(...arguments);
        }
    },

    onExternalBtnClick() {
        if (this.props.newTab) {
            var href = '#id=' + this.resId + '&model=' + this.relation;
            var newWindow = window.open(href, '_blank');
            if (newWindow) {
                newWindow.document.location = href;
            }
        }
        else if (this.props.showPopup) {
            this.openDialog(this.resId);
        }
        else {
            this._super(...arguments);
        }

    }

});

const Many2OneFieldExtractProps = Many2OneField.extractProps;
Many2OneField.extractProps = ({attrs, field}) => {
    return Object.assign(Many2OneFieldExtractProps({attrs, field}), {
        newTab: Boolean(attrs.options.new_tab),
        showPopup: Boolean(attrs.options.show_popup)
    });
};

Many2OneField.props = {
    ...Many2OneField.props,
    newTab: { type: Boolean, optional: true },
    showPopup: { type: Boolean, optional: true },
};
Many2OneField.defaultProps = {
    ...Many2OneField.defaultProps,
    newTab: false,
    showPopup: false,
};


const ReferenceFieldExtractProps = ReferenceField.extractProps;
ReferenceField.extractProps = ({attrs, field}) => {
    return Object.assign(ReferenceFieldExtractProps({attrs, field}), {
        newTab: Boolean(attrs.options.new_tab),
        showPopup: Boolean(attrs.options.show_popup)
    });
};

ReferenceField.props = {
    ...ReferenceField.props,
    newTab: { type: Boolean, optional: true },
    showPopup: { type: Boolean, optional: true },
};

ReferenceField.defaultProps = {
    ...ReferenceField.defaultProps,
    newTab: false,
    showPopup: false,
};


const Many2OneBarcodeFieldExtractProps = Many2OneBarcodeField.extractProps;
Many2OneBarcodeField.extractProps = ({attrs, field}) => {
    return Object.assign(Many2OneBarcodeFieldExtractProps({attrs, field}), {
        newTab: Boolean(attrs.options.new_tab),
        showPopup: Boolean(attrs.options.show_popup)
    });
};

Many2OneBarcodeField.props = {
    ...Many2OneBarcodeField.props,
    newTab: { type: Boolean, optional: true },
    showPopup: { type: Boolean, optional: true },
};

Many2OneBarcodeField.defaultProps = {
    ...Many2OneBarcodeField.defaultProps,
    newTab: false,
    showPopup: false,
};


// const Many2OneAvatarFieldExtractProps = Many2OneAvatarField.extractProps;
// Many2OneAvatarField.extractProps = ({attrs, field}) => {
//     return Object.assign(Many2OneAvatarFieldExtractProps({attrs, field}), {
//         newTab: Boolean(attrs.options.new_tab),
//         showPopup: Boolean(attrs.options.show_popup)
//     });
// };

// Many2OneAvatarField.props = {
//     ...Many2OneAvatarField.props,
//     newTab: { type: Boolean, optional: true },
//     showPopup: { type: Boolean, optional: true },
// };

// Many2OneAvatarField.defaultProps = {
//     ...Many2OneAvatarField.defaultProps,
//     newTab: false,
//     showPopup: false,
// };
