{
    'name':'printer_menu',
    'version': '1.5.19',
    'author': 'Autoronics',
    'summary': 'printer_menu Home Management System',
    'sequence': 1,
    'description':'This is printer_menu home management system software suppored in Odoo',
    'category':'printer_menu',
    'website':'https://www.autoronics.com',
    'depends':['base','website','sale'],

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
        #'views/printer_menu.xml',
        'views/printer_menu_view.xml',
        'views/receipt_report.xml',
        'views/report_order_action.xml',
         
        'views/sale_order_templates.xml',
        'views/sale_order_view.xml',
        
        
        'reports/profile_report.xml',
        'views/report_profile_template.xml',
        'views/profile_views.xml',
        
        # 'views/snippets/s_car_select.xml',
        # 'views/snippets/s_reservation_form.xml',
        # 'reports/links_report_views.xml',
        #'data/antalyahermes.xml'
        
        
       
    ],

    'assets': {
        'web.assets_frontend': [
            # 'printer_menu/static/src/css/intlTelInput.css',
            # 'printer_menu/static/src/css/jquery-clockpicker.min.css',
            # 'printer_menu/static/src/css/style.css',
            # 'printer_menu/static/src/js/jquery-clockpicker.min.js',
            # 'printer_menu/static/src/js/intlTelInput.min.js',
            # 'printer_menu/static/src/js/utils.js',
            # 'printer_menu/static/src/js/reservation.js',
            # 'printer_menu/static/src/js/script.js',
            'printer_menu/static/src/js/thunkableWebviewerExtension.js',
            'printer_menu/static/src/js/print.js',
        ],
        'web.assets_backend': [
            'printer_menu/static/src/js/thunkableWebviewerExtension.js',
            'printer_menu/static/src/css/xml_form.css'
            'printer_menu/static/src/js/print.js',
        ]
    }

}
