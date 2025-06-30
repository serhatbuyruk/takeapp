
console.log("Webstory Profile")
odoo.define('partner.myfunct', function (require) {
    'use strict';
     
    var rpc = require('web.rpc');
    var model = 'webstory.profile';
    
    // Use an empty array to search for all the records
    var domain = [];
    // Use an empty array to read all the fields of the records
    var fields = ['name','webstory_image_small','webstory_image_big'];
    rpc.query({
        model: model,
        method: 'search_read',
        args: [domain, fields],
    }).then(function (data) {console.log(data);}
    ).then(fuction_Demo(111)
    );
    
    });
    
    
    function fuction_Demo(data){
       console.log(data);
    }
    