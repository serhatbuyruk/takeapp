{
    'name':'detection_event',
    'version': '1.5.19',
    'author': 'Autoronics',
    'summary': 'Detection Event System By Autoronics',
    'sequence': 1,
    'description':'This is Detection Event API management system software',
    'category':'detection event',
    'website':'https://www.autoronics.com',
    'depends':['base','web', 'bus' ],

    'data':[
        'security/ir.model.access.csv',        
        'views/detection_event_view.xml',
        #'views/assets.xml',
        #'views/templates.xml',
        #'views/confirmation_wizard_view.xml',
         
        
        
    ],

    'assets': {
        'web.assets_frontend': [
            
            # 'detection_event/static/src/css/style.css',             
            # 'detection_event/static/src/js/script.js',
            'detection_event/static/src/js/thunkableWebviewerExtension.js',
        ],
        'web.assets_backend': [           
            
            #'detection_event/static/src/js/popup.js',
            #'detection_event/static/src/js/popup2.js',
            'detection_event/static/src/js/auto_refresh.js',
            'detection_event/static/src/js/auto_refresh_list.js',
 
            #'detection_event/static/src/js/detection_event_auto_refresh.js',
            
            
            #'detection_event/static/src/css/popup.css',           
            
            #'detection_event/static/src/css/popup_styles.css',
            #'detection_event/static/src/js/detection_popup.js',        
           
            
             
            
    
            # 'detection_event/static/src/js/thunkableWebviewerExtension.js',
            # 'detection_event/static/src/css/xml_form.css'
            
        ],
        'web.assets_qweb': [
            
        ],
    }

}
