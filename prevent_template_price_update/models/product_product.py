from odoo import models, fields, api

class ProductProduct(models.Model):
    _inherit = 'product.product'

    x_variant_price = fields.Float(
        string='Varyant Fiyatı',
        help='Bu alan sadece varyanta özel fiyat tutar. Template fiyatından bağımsızdır.'
    )

    lst_price = fields.Float(
        string='Satış Fiyatı',
        compute='_compute_lst_price',
        inverse='_inverse_lst_price',
        store=True
    )

    @api.depends('x_variant_price')
    def _compute_lst_price(self):
        for rec in self:
            rec.lst_price = rec.x_variant_price or rec.product_tmpl_id.list_price

    def _inverse_lst_price(self):
        for rec in self:
            rec.x_variant_price = rec.lst_price
