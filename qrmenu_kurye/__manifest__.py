{
    'name':'qrmenu kurye',
    'version': '1.5.19',
    'author': 'Autoronics',
    'summary': 'qrmenu_kurye Home Management System',
    'sequence': 1,
    'description':'This is qrmenu_kurye home management system software suppored in Odoo',
    'category':'qrmenu_kurye_kurye',
    'website':'https://www.autoronics.com',
    'depends':['base','website','sale'],

    'data':[
        'security/security.xml',
        'security/ir.model.access.csv', 
        'views/sale_order_inherit_view.xml',
         
       
        
    ],

    'assets': {
        'web.assets_frontend': [
            # 'qrmenu_kurye/static/src/css/intlTelInput.css',
            # 'qrmenu_kurye/static/src/css/jquery-clockpicker.min.css',
            'qrmenu_kurye/static/src/css/style.css',
            # 'qrmenu_kurye/static/src/js/jquery-clockpicker.min.js',
            # 'qrmenu_kurye/static/src/js/intlTelInput.min.js',
            # 'qrmenu_kurye/static/src/js/utils.js',
            # 'qrmenu_kurye/static/src/js/reservation.js',
            # 'qrmenu_kurye_kurye/static/src/js/script.js',
            'qrmenu_kurye/static/src/js/thunkableWebviewerExtension.js', 
 
                
        ],
        'web.assets_backend': [
            'qrmenu_kurye/static/src/js/thunkableWebviewerExtension.js',
            'qrmenu_kurye/static/src/css/xml_form.css',
 
            
        ]
    }

}
