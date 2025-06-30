/** @odoo-module **/

import { registry } from "@web/core/registry";
import { BooleanField } from "@web/views/fields/boolean/boolean_field";
import { Component, xml } from "@odoo/owl";

export class LateOrderBooleanField extends BooleanField {
   setup() {
       
      super.setup();
  }
   static template = "ewelink_modul.LateOrderBooleanField"; // Kullanılacak XML şablonunu belirtir.
}

registry.category("fields").add("late_order_boolean", LateOrderBooleanField);


/* 

Açıklamalar:

import Satırları: Odoo'nun çekirdek modülleri içe aktarılır.

LateOrderBooleanField Sınıfı: BooleanField'den türetilmiştir.

static template: Kullanılacak XML şablonunu belirtir.

registry.category("fields"): Bu bileşeni Odoo'ya kaydeder 
*/