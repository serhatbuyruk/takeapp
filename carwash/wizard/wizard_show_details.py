# -*- coding: utf-8 -*-
import logging
from odoo import models, fields, api, _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)
import base64


class ShowDetails(models.TransientModel):
    _name = "carwash.showdetails"
    _description = "Show Details"

    name = fields.Char(string="Name")
    license_plate = fields.Char(string="License Plate")
    should_send_msg = fields.Boolean(string="Send Message?")
    car_model = fields.Char(string="Car Model")
    car_brand = fields.Char(string="Car Brand")
    phone = fields.Char(string="Mobile Phone")

    def save(self):
        pass

    @api.model
    def default_get(self, fields):
        defaults = super(ShowDetails, self).default_get(fields)

        active_ids = self.env.context.get("active_ids", [])
        # if len(active_ids) == 1:
        # Read active_id from context
        active_id = self.env.context.get('default_active_id')
        if active_id:
            # Fetch the selected record
            profile = self.env["carwash.profile"].browse(active_id)
            # Set values as default
            defaults['name'] = profile.name
            defaults['license_plate'] = profile.license_plate
            defaults['should_send_msg'] = profile.should_send_msg
            defaults['car_model'] = profile.car_model
            defaults['car_brand'] = profile.car_brand
            defaults['phone'] = profile.phone

        return defaults
