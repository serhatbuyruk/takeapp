odoo.define('survey.survey_static_questions', function (require) {
    "use strict";

    var publicWidget = require('web.public.widget');

    publicWidget.registry.SurveyStaticQuestions = publicWidget.Widget.extend({
        selector: '.o_survey_form',
        events: {
            'submit': '_onSurveySubmit',
        },

        _onSurveySubmit: function (ev) {
            var $form = $(ev.currentTarget);
            var surveyData = {
                first_name: $form.find('input[name="first_name"]').val(),
                last_name: $form.find('input[name="last_name"]').val(),
                tc_number: $form.find('input[name="tc_number"]').val(),
                phone_number: $form.find('input[name="phone_number"]').val(),
                birth_date: $form.find('input[name="birth_date"]').val(),
            };
            console.log("Statik Sorular:", surveyData);
        },
    });

    return publicWidget.registry.SurveyStaticQuestions;
});
