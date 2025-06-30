{
    'name':'ewelink_modul',
    'version': '1.5.19',
    'author': 'Autoronics',
    'summary': 'ewelink_modul Home Management System',
    'sequence': 1,
    'description':'This is ewelink_modul home management system software suppored in Odoo',
    'category':'ewelink_modul',
    'website':'https://www.autoronics.com',
    'depends':['base','website','survey'],

    'data':[
        'security/security.xml',
        'security/ir.model.access.csv',
        #'views/all_records_list.xml',
        # 'views/record_item.xml',
        #'views/form_response.xml',
        #'views/sale_order.xml',
        #'views/form_request.xml',
        #'views/car_view.xml',
        #'views/extra.xml',
        #'views/city.xml',
        #'views/snippets/s_booking_widget.xml',
        #'views/snippets/demo/s_cart_product/s_cart_products.xml',
        #'views/snippets/demo/snippets.xml',
        'views/ewelink_modul_view.xml',
        #'views/survey_views.xml',    
        'views/custom_survey_views.xml',  
        #'views/survey_static_fields_form.xml',  # Statik alanları form görünümüne ekleme
        #'views/survey_static_fields_qweb.xml',  # QWeb şablonu ile frontend formu ekleme  
        #'views/late_order_boolean_field.xml'
        # 'views/snippets/s_car_select.xml',
        # 'views/snippets/s_reservation_form.xml',
        # 'reports/links_report_views.xml',
        #'data/antalyahermes.xml'
    ],

    'assets': {
        'web.assets_frontend': [
            # 'ewelink_modul/static/src/css/intlTelInput.css',
            # 'ewelink_modul/static/src/css/jquery-clockpicker.min.css',
             'ewelink_modul/static/src/css/style.css',
            # 'ewelink_modul/static/src/js/jquery-clockpicker.min.js',
            # 'ewelink_modul/static/src/js/intlTelInput.min.js',
            # 'ewelink_modul/static/src/js/utils.js',
            # 'ewelink_modul/static/src/js/reservation.js',
            # 'ewelink_modul/static/src/js/script.js',
            'ewelink_modul/static/src/js/thunkableWebviewerExtension.js',
            #'ewelink_modul/static/src/js/survey_static_questions.js',
        ],
        'web.assets_backend': [
            'ewelink_modul/static/src/js/thunkableWebviewerExtension.js',
            #'ewelink_modul/static/src/css/xml_form.css'
            
            #'ewelink_modul/static/src/js/late_order_boolean_field.js'
           
        ]
    }

}
