{
    'name':'qrmenu',
    'version': '1.5.19',
    'author': 'Autoronics',
    'summary': 'qrmenu Home Management System',
    'sequence': 1,
    'description':'This is qrmenu home management system software suppored in Odoo',
    'category':'qrmenu',
    'website':'https://www.autoronics.com',
    'depends':['base','website'],

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
        'views/qrmenu_view.xml',
        'views/sale_counter_view.xml',
        #'views/sale_order_custom_views.xml',
        
        #'views/whatsapp_snippets.xml',
        'views/qr_code_generator.xml',
        #'views/custom_qr_viewer.xml',
        #'views/custom_website_template.xml',
        'views/menus.xml',
        #'views/custom_whatsapp_location_snippet.xml',
        
       

        # 'views/snippets/s_car_select.xml',
        # 'views/snippets/s_reservation_form.xml',
        # 'reports/links_report_views.xml',
        #'data/antalyahermes.xml'
        
    ],

    'assets': {
        'web.assets_frontend': [
            # 'qrmenu/static/src/css/intlTelInput.css',
            # 'qrmenu/static/src/css/jquery-clockpicker.min.css',
            'qrmenu/static/src/css/style.css',
            # 'qrmenu/static/src/js/jquery-clockpicker.min.js',
            # 'qrmenu/static/src/js/intlTelInput.min.js',
            # 'qrmenu/static/src/js/utils.js',
            # 'qrmenu/static/src/js/reservation.js',
            # 'qrmenu/static/src/js/script.js',
            'qrmenu/static/src/js/thunkableWebviewerExtension.js', 
            'qrmenu/static/src/js/whatsapp.js',
            'qrmenu/static/src/js/WhatsappLocationButton.js',          
        ],
        'web.assets_backend': [
            'qrmenu/static/src/js/thunkableWebviewerExtension.js',
            'qrmenu/static/src/css/xml_form.css',
            'qrmenu/static/src/js/sound.js',
            
        ]
    }

}
