odoo.define('web.web_widget_mp3_player', function (require) {
    "use strict";

    var field_registry = require('web.field_registry');
    // var Field = field_registry.get('char');

    var AbstractField = require('web.AbstractField');

    var FieldMp3Player = AbstractField.extend({
        template: 'FieldMp3Player',
        widget_class: 'oe_form_field_mp3_player',

        _renderReadonly: function () {
            var show_value = this._formatValue(this.value);
            this.$el.find("source").attr("src", show_value);
            this.$el.show();
            this.$el.unbind( "change" );
            this.$el.find("source").unbind( "change" );
        },

        _getValue: function () {
            var $input = this.$el.find('input');
            return $input.val();
        },

        _renderEdit: function () {
            var show_value = this.value;
            var $input = this.$el.find('input');
            $input.val(show_value);
            this.$input = $input;
        },
        _doDebouncedAction : function () {

        }

    });

    field_registry
        .add('mp3player', FieldMp3Player);

    return {
        FieldMp3Player: FieldMp3Player
    };


});