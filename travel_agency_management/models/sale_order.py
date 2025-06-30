from odoo import models, fields, api, _
from odoo.exceptions import UserError

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    # --- Custom Fields for the Travel Form ---
    departure_date = fields.Date(string="Departure Date")
    return_date = fields.Date(string="Return Date")
    from_country_id = fields.Many2one('res.country', string="From Country")
    from_airport_id = fields.Many2one('travel.airport', string="From Airport")
    to_country_id = fields.Many2one('res.country', string="To Country")
    to_airport_id = fields.Many2one('travel.airport', string="To Airport")
    
    travel_direction = fields.Char(string="Direction", compute='_compute_travel_direction', store=True)

    ticket_company_id = fields.Many2one('res.partner', string="Airline", domain="[('supplier_rank', '>', 0)]")
    ticket_purchase_date = fields.Date(string="Ticket Purchase Date")
    ticket_number = fields.Char(string="Ticket Number")
    ticket_adults = fields.Integer(string="Adults (Ticket)", default=0)
    ticket_children = fields.Integer(string="Children (Ticket)", default=0)
    ticket_infants = fields.Integer(string="Infants (Ticket)", default=0)
    ticket_note = fields.Text(string="Note (Ticket)")
    ticket_fare = fields.Float(string="Fare")
    ticket_tax = fields.Float(string="Tax")
    ticket_purchase_total = fields.Float(string="Purchase Total (Ticket)", compute='_compute_ticket_purchase_total', store=True)
    ticket_sale_price = fields.Float(string="Sale Price (Ticket)")
    ticket_profit_percent = fields.Float(string="Profit % (Ticket)")

    hotel_company_id = fields.Many2one('res.partner', string="Hotel", domain="[('supplier_rank', '>', 0)]")
    hotel_room_count = fields.Integer(string="Room Count", default=0)
    hotel_adults = fields.Integer(string="Adults (Hotel)", default=0)
    hotel_children = fields.Integer(string="Children (Hotel)", default=0)
    hotel_infants = fields.Integer(string="Infants (Hotel)", default=0)
    hotel_meal_breakfast = fields.Boolean(string="Breakfast")
    hotel_meal_lunch = fields.Boolean(string="Lunch")
    hotel_meal_dinner = fields.Boolean(string="Dinner")
    hotel_note = fields.Text(string="Note (Hotel)")
    hotel_purchase_price = fields.Float(string="Purchase Price (Hotel)")
    hotel_sale_price = fields.Float(string="Sale Price (Hotel)")
    hotel_deadline = fields.Date(string="Deadline (Hotel)")

    transfer_company_id = fields.Many2one('res.partner', string="Transfer Company", domain="[('supplier_rank', '>', 0)]")
    transfer_type = fields.Selection([('individual', 'Individual'), ('group', 'Group')], string="Transfer Type", default='individual')
    transfer_from = fields.Char(string="Transfer From")
    transfer_to = fields.Char(string="Transfer To")
    transfer_datetime = fields.Datetime(string="Transfer Date/Time")
    transfer_note = fields.Text(string="Note (Transfer)")
    transfer_purchase_price = fields.Float(string="Purchase Price (Transfer)")
    transfer_sale_price = fields.Float(string="Sale Price (Transfer)")
    transfer_deadline = fields.Date(string="Deadline (Transfer)")

    insurance_company_id = fields.Many2one('res.partner', string="Insurance Company", domain="[('supplier_rank', '>', 0)]")
    insurance_date = fields.Date(string="Insurance Date")
    insurance_country_id = fields.Many2one('res.country', string="Insurance Country")
    insurance_note = fields.Text(string="Note (Insurance)")
    insurance_purchase_price = fields.Float(string="Purchase Price (Insurance)")
    insurance_sale_price = fields.Float(string="Sale Price (Insurance)")
    
    tour_package_id = fields.Many2one('product.product', string="Tour Package", domain="[('type', '=', 'service')]")
    tour_company_id = fields.Many2one('res.partner', string="Tour Company", domain="[('supplier_rank', '>', 0)]")
    tour_note = fields.Text(string="Note (Tour)")
    tour_purchase_price = fields.Float(string="Purchase Price (Tour)")
    tour_sale_price = fields.Float(string="Sale Price (Tour)")
    tour_deadline = fields.Date(string="Deadline (Tour)")

    visa_company_id = fields.Many2one('res.partner', string="Visa Service Company", domain="[('supplier_rank', '>', 0)]")
    visa_note = fields.Text(string="Note (Visa)")
    visa_purchase_price = fields.Float(string="Purchase Price (Visa)")
    visa_sale_price = fields.Float(string="Sale Price (Visa)")
    
    other_service_name = fields.Char(string="Other Service Name")
    other_note = fields.Text(string="Note (Other)")
    other_purchase_price = fields.Float(string="Purchase Price (Other)")
    other_sale_price = fields.Float(string="Sale Price (Other)")
    
    total_purchase_price = fields.Monetary(string="Total Purchase", compute='_compute_travel_totals', store=True, currency_field='currency_id')
    total_sale_price = fields.Monetary(string="Total Sales", compute='_compute_travel_totals', store=True, currency_field='currency_id')
    total_profit = fields.Monetary(string="Total Profit", compute='_compute_travel_totals', store=True, currency_field='currency_id')

    invoice_payment_state = fields.Selection(
        related='invoice_ids.payment_state',
        string="Invoice Payment Status",
        store=True,
    )

    ##

    @api.depends('from_airport_id.code', 'to_airport_id.code')
    def _compute_travel_direction(self):
        for order in self:
            direction_parts = []
            if order.from_airport_id:
                direction_parts.append(order.from_airport_id.code)
            if order.to_airport_id:
                direction_parts.append(order.to_airport_id.code)
            order.travel_direction = ' / '.join(direction_parts) if direction_parts else ''

    @api.depends('ticket_fare', 'ticket_tax')
    def _compute_ticket_purchase_total(self):
        for order in self:
            order.ticket_purchase_total = order.ticket_fare + order.ticket_tax

    @api.depends(
        'ticket_sale_price', 'hotel_sale_price', 'transfer_sale_price', 
        'insurance_sale_price', 'tour_sale_price', 'visa_sale_price', 'other_sale_price',
        'ticket_purchase_total', 'hotel_purchase_price', 'transfer_purchase_price',
        'insurance_purchase_price', 'tour_purchase_price', 'visa_purchase_price', 'other_purchase_price'
    )
    def _compute_travel_totals(self):
        for order in self:
            purchase_price = (order.ticket_purchase_total + order.hotel_purchase_price + order.transfer_purchase_price + order.insurance_purchase_price + order.tour_purchase_price + order.visa_purchase_price + order.other_purchase_price)
            sale_price = (order.ticket_sale_price + order.hotel_sale_price + order.transfer_sale_price + order.insurance_sale_price + order.tour_sale_price + order.visa_sale_price + order.other_sale_price)
            
            order.total_purchase_price = purchase_price
            order.total_sale_price = sale_price
            order.total_profit = sale_price - purchase_price

    def _update_travel_order_line(self):
        self.ensure_one()
        tour_product = self.env.ref('travel_agency_management.product_tour_sale', raise_if_not_found=False)
        if not tour_product:
            return

        existing_line = self.order_line.filtered(lambda l: l.product_id == tour_product)
        line_vals = {
            'product_id': tour_product.id,
            'name': _('Travel Services for Order %s') % self.name,
            'product_uom_qty': 1,
            'price_unit': self.total_sale_price,
            'order_id': self.id,
        }

        if existing_line:
            if self.total_sale_price <= 0:
                existing_line.unlink()
            else:
                existing_line.write(line_vals)
        elif self.total_sale_price > 0:
            self.order_line.filtered(lambda l: l.product_id != tour_product).unlink()
            self.env['sale.order.line'].create(line_vals)

    @api.model_create_multi
    def create(self, vals_list):
        orders = super().create(vals_list)
        for order in orders:
            order._compute_travel_totals()
            order._update_travel_order_line()
        return orders

    def write(self, vals):
        res = super().write(vals)
        price_fields = [
            'ticket_sale_price', 'hotel_sale_price', 'transfer_sale_price', 
            'insurance_sale_price', 'tour_sale_price', 'visa_sale_price', 'other_sale_price',
            'ticket_fare', 'ticket_tax', 'hotel_purchase_price', 'transfer_purchase_price',
            'insurance_purchase_price', 'tour_purchase_price', 'visa_purchase_price', 'other_purchase_price'
        ]
        if any(field in vals for field in price_fields):
            for order in self:
                order._update_travel_order_line()
        return res

    def button_calculate_profit_percent(self):
        self.ensure_one()
        if self.ticket_sale_price and self.ticket_purchase_total:
            profit = self.ticket_sale_price - self.ticket_purchase_total
            if self.ticket_purchase_total > 0:
                self.ticket_profit_percent = (profit / self.ticket_purchase_total) * 100
        return True

    def action_create_travel_invoice(self):
        """
        This is the method our "Invoice" button will call.
        """
        self.ensure_one()
        # Ensure the line is up-to-date before creating the invoice
        self._update_travel_order_line()

        # Call the standard Odoo method to create invoices
        invoices = self._create_invoices()
        
        # Odoo's standard action to view the created invoices.
        return self.action_view_invoice()
        

    # --- NEW METHOD to view existing invoices ---
    def action_view_invoice(self):
        """
        This is the method our "View Invoice" button will call.
        It finds and displays the invoices associated with this sales order.
        """
        return super().action_view_invoice()