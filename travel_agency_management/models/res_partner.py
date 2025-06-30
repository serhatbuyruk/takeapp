from odoo import models, fields, api

class ResPartner(models.Model):
    _inherit = 'res.partner'

    passport_image = fields.Image(string="Passport Image", max_width=512, max_height=512)
    family_member_ids = fields.One2many('res.partner', 'main_contact_id', string="Family Members")
    main_contact_id = fields.Many2one('res.partner', string="Main Contact", index=True, ondelete='cascade')
    
    service_type_ids = fields.Many2many(
        'travel.service.type', 
        string="Services",
        help="Service types associated with this contact (Ticket, Hotel, etc.)"
    )

    sale_order_count_custom = fields.Integer(string="Order Count", compute='_compute_financial_summary')
    total_sale_value = fields.Monetary(string="Total Sales", compute='_compute_financial_summary')
    total_purchase_value = fields.Monetary(string="Total Purchase", compute='_compute_financial_summary')
    total_profit_value = fields.Monetary(string="Total Profit", compute='_compute_financial_summary')

    def _compute_financial_summary(self):
        SaleOrder = self.env['sale.order']
        for partner in self:
            orders = SaleOrder.search([
                ('partner_id', '=', partner.id),
                ('state', 'in', ['sale', 'done'])
            ])
            partner.sale_order_count_custom = len(orders)
            partner.total_sale_value = sum(orders.mapped('total_sale_price'))
            partner.total_purchase_value = sum(orders.mapped('total_purchase_price'))
            partner.total_profit_value = sum(orders.mapped('total_profit'))
