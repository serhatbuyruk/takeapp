# travel_agency_management/models/sale_order.py

from odoo import models, fields, api, _
from odoo.exceptions import UserError
import json
import logging

_logger = logging.getLogger(__name__)

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

    ticket_company_id = fields.Many2one('res.partner', string="Airline", domain="[('service_type_ids', 'in', [1])]")
    ticket_purchase_date = fields.Date(string="Ticket Purchase Date")
    ticket_number = fields.Char(string="Ticket Number")
    ticket_adults = fields.Integer(string="Adults (Ticket)", default=0)
    ticket_children = fields.Integer(string="Children (Ticket)", default=0)
    ticket_infants = fields.Integer(string="Infants (Ticket)", default=0)
    ticket_note = fields.Text(string="Note (Ticket)")
    ticket_fare = fields.Float(string="Fare")
    ticket_tax = fields.Float(string="Tax")
    extra_fare = fields.Float(string="Extra")
    ticket_purchase_total = fields.Float(string="Purchase Total (Ticket)", compute='_compute_ticket_purchase_total', store=True)
    ticket_sale_price = fields.Float(string="Sale Price (Ticket)")
    ticket_profit_percent = fields.Float(string="Profit % (Ticket)")
    ticket_profit = fields.Float(string="Profit (Ticket)", compute='_compute_service_profits', store=True)

    hotel_company_id = fields.Many2one('res.partner', string="Hotel", domain="[('service_type_ids', 'in', [2])]")
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
    hotel_first_date = fields.Date(string="First Date (Hotel)")
    hotel_deadline = fields.Date(string="Deadline (Hotel)")
    hotel_profit = fields.Float(string="Profit (Hotel)", compute='_compute_service_profits', store=True)

    transfer_company_id = fields.Many2one('res.partner', string="Transfer Company", domain="[('service_type_ids', 'in', [3])]")
    transfer_type = fields.Selection([('individual', 'Individual'), ('group', 'Group')], string="Transfer Type", default='individual')
    transfer_from = fields.Char(string="Transfer From")
    transfer_to = fields.Char(string="Transfer To")
    transfer_datetime = fields.Datetime(string="Transfer Date/Time")
    transfer_note = fields.Text(string="Note (Transfer)")
    transfer_purchase_price = fields.Float(string="Purchase Price (Transfer)")
    transfer_sale_price = fields.Float(string="Sale Price (Transfer)")
    transfer_deadline = fields.Date(string="Deadline (Transfer)")
    transfer_profit = fields.Float(string="Profit (Transfer)", compute='_compute_service_profits', store=True)

    insurance_company_id = fields.Many2one('res.partner', string="Insurance Company", domain="[('service_type_ids', 'in', [5])]")
    insurance_date = fields.Date(string="Insurance Date")
    insurance_country_id = fields.Many2one('res.country', string="Insurance Country")
    insurance_note = fields.Text(string="Note (Insurance)")
    insurance_purchase_price = fields.Float(string="Purchase Price (Insurance)")
    insurance_sale_price = fields.Float(string="Sale Price (Insurance)")
    insurance_profit = fields.Float(string="Profit (Insurance)", compute='_compute_service_profits', store=True)

    tour_package_id = fields.Many2one('product.product', string="Tour Package", domain="[('type', '=', 'service')]")
    tour_company_id = fields.Many2one('res.partner', string="Tour Company", domain="[('service_type_ids', 'in', [6])]")
    tour_note = fields.Text(string="Note (Tour)")
    tour_purchase_price = fields.Float(string="Purchase Price (Tour)")
    tour_sale_price = fields.Float(string="Sale Price (Tour)")
    tour_deadline = fields.Date(string="Deadline (Tour)")
    tour_profit = fields.Float(string="Profit (Tour)", compute='_compute_service_profits', store=True)

    visa_company_id = fields.Many2one('res.partner', string="Visa Service Company", domain="[('service_type_ids', 'in', [4])]")
    visa_note = fields.Text(string="Note (Visa)")
    visa_purchase_price = fields.Float(string="Purchase Price (Visa)")
    visa_sale_price = fields.Float(string="Sale Price (Visa)")
    visa_profit = fields.Float(string="Profit (Visa)", compute='_compute_service_profits', store=True)
    
    other_service_name = fields.Char(string="Other Service Name")
    other_note = fields.Text(string="Note (Other)")
    other_purchase_price = fields.Float(string="Purchase Price (Other)")
    other_sale_price = fields.Float(string="Sale Price (Other)")
    other_profit = fields.Float(string="Profit (Other)", compute='_compute_service_profits', store=True)

    total_purchase_price = fields.Monetary(string="Total Purchase", compute='_compute_travel_totals', store=True, currency_field='currency_id')
    total_sale_price = fields.Monetary(string="Total Sales", compute='_compute_travel_totals', store=True, currency_field='currency_id')
    total_profit = fields.Monetary(string="Total Profit", compute='_compute_travel_totals', store=True, currency_field='currency_id')

    purchase_order_ids = fields.One2many('purchase.order', 'origin_sale_order_id', string='Purchase Orders')
    purchase_count = fields.Integer(string='PO Count', compute='_compute_purchase_count', store=True)

    invoice_payment_state = fields.Selection(
        related='invoice_ids.payment_state',
        string="Invoice Payment Status",
        store=True,
    )

    family_member_ids = fields.Many2many(
        'res.partner',
        string="Family Members",
        help="Main contact and their family members, automatically populated. Can be edited manually."
    )

    invoice_amount_residual = fields.Monetary(
        string='Amount Due',
        compute='_compute_invoice_amounts', # Metot ismi daha genel olacak şekilde değiştirildi
        store=True,
        currency_field='currency_id'
    )
    
    # =======================================================
    # YENİ EKLENDİ: Ödenen tutar alanı
    # =======================================================
    invoice_amount_paid = fields.Monetary(
        string='Amount Paid',
        compute='_compute_invoice_amounts', # Aynı metot ile hesaplanacak
        store=True,
        currency_field='currency_id'
    )

    partner_credit_balance = fields.Monetary(
        string='Customer Credit',
        compute='_compute_partner_credit',
        help="Shows the outstanding credit amount for this customer. This is the money the customer has paid in excess."
    )

    has_draft_invoice = fields.Boolean(
        string="Has Draft Invoice",
        compute='_compute_has_draft_invoice',
        help="True if the sales order has at least one invoice in draft state."
    )

    
    @api.depends('purchase_order_ids')
    def _compute_purchase_count(self):
        for order in self:
            order.purchase_count = len(order.purchase_order_ids)

    def _create_vendor_purchase_orders(self):
        """
        Tedarikçiler için Satınalma Siparişlerini ve faturalarını oluşturur.
        Bu metot, müşteri faturası onaylandığında tetiklenir.
        """
        self.ensure_one()
        _logger.info(f"Attempting to create vendor POs for Sale Order {self.name}.")

        if self.purchase_count > 0:
            _logger.warning(f"Purchase orders already exist for {self.name}. Aborting.")
            return

        purchase_product = self.env.ref('travel_agency_management.product_service_purchase')
        
        services_to_process = {
            'Ticket': (self.ticket_company_id, self.ticket_purchase_total),
            'Hotel': (self.hotel_company_id, self.hotel_purchase_price),
            'Transfer': (self.transfer_company_id, self.transfer_purchase_price),
            'Insurance': (self.insurance_company_id, self.insurance_purchase_price),
            'Tour': (self.tour_company_id, self.tour_purchase_price),
            'Visa': (self.visa_company_id, self.visa_purchase_price),
        }

        vendor_lines = {}

        for service_name, (vendor, price) in services_to_process.items():
            if vendor and price > 0:
                if vendor.id not in vendor_lines: vendor_lines[vendor.id] = []
                
                line_vals = {
                    'product_id': purchase_product.id,
                    'name': f"{service_name} service for SO {self.name}",
                    'product_qty': 1,
                    'price_unit': price,
                    'date_planned': self.departure_date or fields.Date.today(),
                }
                vendor_lines[vendor.id].append((0, 0, line_vals))
        
        if not vendor_lines:
            _logger.info(f"No valid vendor services to create POs for {self.name}.")
            return

        created_pos = self.env['purchase.order']
        for vendor_id, lines in vendor_lines.items():
            po_vals = {
                'partner_id': vendor_id,
                'currency_id': self.currency_id.id,  # <-- YENİ EKLENEN SATIR
                'origin': self.name,
                'origin_sale_order_id': self.id,
                'order_line': lines,
            }
            try:
                po = self.env['purchase.order'].create(po_vals)
                po.button_confirm()
                _logger.info(f"Confirmed Purchase Order {po.name}.")

                po.action_create_invoice()
                
                draft_bill = po.invoice_ids.filtered(lambda inv: inv.state == 'draft')
                if draft_bill:
                    # =======================================================
                    # GÜNCELLENEN SATIR BURASI
                    # Direkt atama yerine Odoo'nun write() metodunu kullanıyoruz.
                    # =======================================================
                    draft_bill.write({'invoice_date': fields.Date.today()})
                    
                    draft_bill.action_post()
                    _logger.info(f"Posted Vendor Bill {draft_bill.name} for PO {po.name}.")
                else:
                    _logger.warning(f"Could not find a draft bill to post for PO {po.name}.")

                created_pos |= po
            except Exception as e:
                _logger.error(f"Failed to create/process PO/Bill for vendor {vendor_id} from SO {self.name}: {e}")
                self.message_post(body=_("Failed to create purchase order/bill for vendor ID %s. Error: %s") % (vendor_id, e))
        
        if created_pos:
            self.message_post(body=_("Created %s Purchase Order(s): %s") % (len(created_pos), ", ".join(created_pos.mapped('name'))))

    def action_view_purchase_orders(self):
        self.ensure_one()
        return {
            'name': _('Purchase Orders'),
            'type': 'ir.actions.act_window',
            'res_model': 'purchase.order',
            'view_mode': 'tree,form',
            'domain': [('id', 'in', self.purchase_order_ids.ids)],
        }


    def action_confirm_and_view_invoice(self):
        self.ensure_one()
        draft_invoices = self.invoice_ids.filtered(lambda inv: inv.state == 'draft')
        if draft_invoices:
            draft_invoices.action_post()
        
        self._create_vendor_purchase_orders() # <-- BU SATIRI EKLEYİN
        
        return self.action_view_invoice()

    @api.depends('invoice_ids.state')
    def _compute_has_draft_invoice(self):
        for order in self:
            order.has_draft_invoice = bool(order.invoice_ids.filtered(lambda inv: inv.state == 'draft'))

    @api.onchange('partner_id')
    def _onchange_partner_id_set_family_members(self):
        if self.partner_id:
            members = self.partner_id.family_member_ids
            self.family_member_ids = [(6, 0, members.ids)]
        else:
            self.family_member_ids = [(5, 0, 0)]

    @api.depends('total_sale_price')
    def _compute_partner_credit(self):
        for order in self:
            if order.partner_id:
                partner = order.partner_id
                balance = partner.debit - partner.credit
                if balance < 0:
                    order.partner_credit_balance = 0.0
                else:
                    order.partner_credit_balance = -balance
            else:
                order.partner_credit_balance = 0.0

    # =======================================================
    # GÜNCELLENDİ: Hem ödenen hem de kalan tutarı hesaplayan
    # tek bir metot oluşturuldu.
    # =======================================================
    @api.depends('invoice_ids.amount_residual', 'invoice_ids.amount_total')
    def _compute_invoice_amounts(self):
        for order in self:
            total_invoiced = sum(order.invoice_ids.mapped('amount_total'))
            amount_residual = sum(order.invoice_ids.mapped('amount_residual'))
            order.invoice_amount_residual = amount_residual
            order.invoice_amount_paid = total_invoiced - amount_residual

    @api.depends('from_airport_id.code', 'to_airport_id.code')
    def _compute_travel_direction(self):
        for order in self:
            direction_parts = []
            if order.from_airport_id:
                direction_parts.append(order.from_airport_id.code)
            if order.to_airport_id:
                direction_parts.append(order.to_airport_id.code)
            order.travel_direction = ' / '.join(direction_parts) if direction_parts else ''

    @api.depends('ticket_fare', 'ticket_tax', 'extra_fare')
    def _compute_ticket_purchase_total(self):
        for order in self:
            order.ticket_purchase_total = order.ticket_fare + order.ticket_tax + order.extra_fare

    @api.depends(
        'ticket_sale_price', 'ticket_purchase_total',
        'hotel_sale_price', 'hotel_purchase_price',
        'transfer_sale_price', 'transfer_purchase_price',
        'insurance_sale_price', 'insurance_purchase_price',
        'tour_sale_price', 'tour_purchase_price',
        'visa_sale_price', 'visa_purchase_price',
        'other_sale_price', 'other_purchase_price'
    )
    def _compute_service_profits(self):
        for order in self:
            order.ticket_profit = order.ticket_sale_price - order.ticket_purchase_total
            order.hotel_profit = order.hotel_sale_price - order.hotel_purchase_price
            order.transfer_profit = order.transfer_sale_price - order.transfer_purchase_price
            order.insurance_profit = order.insurance_sale_price - order.insurance_purchase_price
            order.tour_profit = order.tour_sale_price - order.tour_purchase_price
            order.visa_profit = order.visa_sale_price - order.visa_purchase_price
            order.other_profit = order.other_sale_price - order.other_purchase_price

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
            'ticket_fare', 'ticket_tax', 'extra_fare', 'hotel_purchase_price', 'transfer_purchase_price',
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
        self.ensure_one()
        self._update_travel_order_line()
        invoices = self._create_invoices()
        return self.action_view_invoice()

    def action_view_invoice(self):
        return super().action_view_invoice()

    def action_view_payments(self):
        self.ensure_one()
        invoices = self.invoice_ids.filtered(lambda inv: inv.move_type == 'out_invoice')
        if not invoices:
            raise UserError(_("No customer invoices found for this order."))
        receivable_lines = invoices.line_ids.filtered(
            lambda line: line.account_id.account_type == 'asset_receivable'
        )
        reconciled_lines = receivable_lines.mapped('matched_debit_ids.debit_move_id') + \
                           receivable_lines.mapped('matched_credit_ids.credit_move_id')
        payment_ids = reconciled_lines.mapped('payment_id').ids
        if not payment_ids:
            raise UserError(_("No payments found for this order."))
        return {
            'name': _('Payments for Order %s') % self.name,
            'type': 'ir.actions.act_window',
            'res_model': 'account.payment',
            'view_mode': 'tree,form',
            'domain': [('id', 'in', list(set(payment_ids)))],
            'target': 'current',
        }