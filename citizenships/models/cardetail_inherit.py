from odoo import models, fields

class productTemplateInherit(models.Model):
    _inherit = 'product.template'

    product_type_selection = fields.Selection([('car','Car'),('yatch','Yatch'),('home','Home')],
                                    string="Product type"
                                    )
    plate = fields.Char(string="Plate")
    mark_model = fields.Char(string="Mark And Model")
    car_color = fields.Char(string="Car Color")
    car_year = fields.Char(string="Car Year")
    car_km = fields.Char(string="Car KM")

class productProductInherit(models.Model):
    _inherit = 'product.product'

    product_type_selection = fields.Selection([('car','Car'),('yatch','Yatch'),('home','Home')],
                                    string="Product type"
                                    )
    plate = fields.Char(string="Plate")
    mark_model = fields.Char(string="Mark And Model")
    car_color = fields.Char(string="Car Color")
    car_year = fields.Char(string="Car Year")
    car_km = fields.Char(string="Car KM")
    