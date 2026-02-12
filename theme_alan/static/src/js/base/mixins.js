/** @odoo-module alias=theme_alan.mixins **/

import { qweb } from 'web.core';

var alanTemplate = {
    getStaticTemplate:function(template, context){
        return qweb.render(template, { data: context });
    }
}

export default {
    alanTemplate:alanTemplate,
}
