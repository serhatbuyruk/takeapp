#!/bin/bash

# ==============================================================================
# Odoo 16 Travel Agency Management Module Creation Script (v1.5 - Bugfix)
#
# This script creates the 'travel_agency_management' module.
#
# Revisions:
# - FIXED: "Element cannot be located" error in sale_order_views.xml.
#   The XPath expressions were reordered to avoid trying to modify
#   an element that was previously removed. The approach is now to
#   replace the whole content of the sheet for a cleaner and more
#   robust inheritance.
#
# Author: Your Name (and AI Assistant)
# Version: 16.0.1.6.0
# ==============================================================================

MODULE_NAME="travel_agency_management"

# Check if the module directory already exists
if [ -d "$MODULE_NAME" ]; then
  echo "ERROR: A directory named '$MODULE_NAME' already exists."
  echo "Please delete or rename the existing directory and try again."
  exit 1
fi

echo "Creating Odoo module '$MODULE_NAME' (English, Rev 1.5)..."

# 1. Create the main directory structure
echo "-> Creating directory structure..."
mkdir -p $MODULE_NAME/{models,views,security,data,static/description}

# 2. Create main __init__.py and __manifest__.py files
echo "-> Creating __init__.py and __manifest__.py files..."

cat << 'EOF' > $MODULE_NAME/__init__.py
from . import models
EOF

cat << 'EOF' > $MODULE_NAME/__manifest__.py
{
    'name': 'Travel Agency Management',
    'version': '16.0.1.6.0',
    'summary': 'A comprehensive module to manage a travel agency business.',
    'description': """
        Extends Sales, Contacts and Accounting modules for Travel Agency needs.
        - Detailed, custom Sale Order form matching specific layout.
        - Dependent airport dropdowns based on selected country.
        - Calculates total purchase, sale, and profit on Sales Orders.
        - Enhances Contacts with Passport Information and Family Members.
        - Provides a financial summary view for customers.
    """,
    'author': 'Your Name',
    'website': 'https://www.yourwebsite.com',
    'category': 'Services/Travel',
    'depends': [
        'base', 
        'sale_management',
        'contacts',
        'account',
    ],
    'data': [
        'security/ir.model.access.csv',
        'data/travel_service_type_data.xml',
        'data/travel_airport_data.xml',
        'views/res_partner_views.xml',
        'views/sale_order_views.xml',
        'views/main_menus.xml',
    ],
    'assets': {},
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
}
EOF

# 3. Create model files
echo "-> Creating model files..."

cat << 'EOF' > $MODULE_NAME/models/__init__.py
from . import travel_models
from . import res_partner
from . import sale_order
EOF

cat << 'EOF' > $MODULE_NAME/models/travel_models.py
from odoo import models, fields

class TravelServiceType(models.Model):
    _name = 'travel.service.type'
    _description = 'Travel Service Type'

    name = fields.Char(string="Service Name", required=True, translate=True)

class TravelAirport(models.Model):
    _name = 'travel.airport'
    _description = 'Airport'
    _order = 'name'

    name = fields.Char(string="Airport Name", required=True)
    code = fields.Char(string="IATA Code", required=True)
    country_id = fields.Many2one('res.country', string="Country", required=True)

    def name_get(self):
        result = []
        for record in self:
            name = f'[{record.code}] {record.name}'
            result.append((record.id, name))
        return result
EOF

cat << 'EOF' > $MODULE_NAME/models/res_partner.py
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
EOF

cat << 'EOF' > $MODULE_NAME/models/sale_order.py
from odoo import models, fields, api

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    departure_date = fields.Date(string="Departure Date")
    return_date = fields.Date(string="Return Date")
    from_country_id = fields.Many2one('res.country', string="From Country")
    from_airport_id = fields.Many2one('travel.airport', string="From Airport")
    to_country_id = fields.Many2one('res.country', string="To Country")
    to_airport_id = fields.Many2one('travel.airport', string="To Airport")

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

    @api.depends('ticket_fare', 'ticket_tax')
    def _compute_ticket_purchase_total(self):
        for order in self:
            order.ticket_purchase_total = order.ticket_fare + order.ticket_tax

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

    @api.depends(
        'ticket_purchase_total', 'ticket_sale_price',
        'hotel_purchase_price', 'hotel_sale_price',
        'transfer_purchase_price', 'transfer_sale_price',
        'insurance_purchase_price', 'insurance_sale_price',
        'tour_purchase_price', 'tour_sale_price',
        'visa_purchase_price', 'visa_sale_price',
        'other_purchase_price', 'other_sale_price'
    )
    def _compute_travel_totals(self):
        for order in self:
            purchase_total = (
                order.ticket_purchase_total +
                order.hotel_purchase_price +
                order.transfer_purchase_price +
                order.insurance_purchase_price +
                order.tour_purchase_price +
                order.visa_purchase_price +
                order.other_purchase_price
            )
            sale_total = (
                order.ticket_sale_price +
                order.hotel_sale_price +
                order.transfer_sale_price +
                order.insurance_sale_price +
                order.tour_sale_price +
                order.visa_sale_price +
                order.other_sale_price
            )
            order.total_purchase_price = purchase_total
            order.total_sale_price = sale_total
            order.total_profit = sale_total - purchase_total

    def button_calculate_profit_percent(self):
        self.ensure_one()
        if self.ticket_sale_price and self.ticket_purchase_total:
            profit = self.ticket_sale_price - self.ticket_purchase_total
            if self.ticket_purchase_total > 0:
                self.ticket_profit_percent = (profit / self.ticket_purchase_total) * 100
        return True
EOF

# 4. Create security file
echo "-> Creating security file (ir.model.access.csv)..."
cat << 'EOF' > $MODULE_NAME/security/ir.model.access.csv
id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink
access_travel_service_type_user,access.travel.service.type.user,model_travel_service_type,base.group_user,1,1,1,1
access_travel_airport_user,access.travel.airport.user,model_travel_airport,base.group_user,1,1,1,1
EOF

# 5. Create data files
echo "-> Creating data files..."
cat << 'EOF' > $MODULE_NAME/data/travel_service_type_data.xml
<odoo>
    <data noupdate="1">
        <record id="service_type_ticket" model="travel.service.type"><field name="name">Ticket</field></record>
        <record id="service_type_hotel" model="travel.service.type"><field name="name">Hotel</field></record>
        <record id="service_type_transfer" model="travel.service.type"><field name="name">Transfer</field></record>
        <record id="service_type_visa" model="travel.service.type"><field name="name">Visa</field></record>
        <record id="service_type_insurance" model="travel.service.type"><field name="name">Insurance</field></record>
        <record id="service_type_tourpackage" model="travel.service.type"><field name="name">Tour Package</field></record>
    </data>
</odoo>
EOF

cat << 'EOF' > $MODULE_NAME/data/travel_airport_data.xml
<odoo>
    <data noupdate="1">
        <record id="airport_ist" model="travel.airport"><field name="name">Istanbul Airport</field><field name="code">IST</field><field name="country_id" ref="base.tr"/></record>
        <record id="airport_saw" model="travel.airport"><field name="name">Sabiha Gokcen International Airport</field><field name="code">SAW</field><field name="country_id" ref="base.tr"/></record>
        <record id="airport_esb" model="travel.airport"><field name="name">Esenboga Airport</field><field name="code">ESB</field><field name="country_id" ref="base.tr"/></record>
        <record id="airport_gyd" model="travel.airport"><field name="name">Heydar Aliyev International Airport</field><field name="code">GYD</field><field name="country_id" ref="base.az"/></record>
        <record id="airport_svx" model="travel.airport"><field name="name">Koltsovo Airport</field><field name="code">SVX</field><field name="country_id" ref="base.ru"/></record>
        <record id="airport_dme" model="travel.airport"><field name="name">Domodedovo International Airport</field><field name="code">DME</field><field name="country_id" ref="base.ru"/></record>
    </data>
</odoo>
EOF

# 6. Create view files
echo "-> Creating view files..."

cat << 'EOF' > $MODULE_NAME/views/res_partner_views.xml
<odoo>
    <record id="view_partner_form_travel" model="ir.ui.view">
        <field name="name">res.partner.form.travel</field>
        <field name="model">res.partner</field>
        <field name="inherit_id" ref="base.view_partner_form"/>
        <field name="arch" type="xml">
            <field name="vat" position="after">
                <field name="service_type_ids" widget="many2many_tags" options="{'color_field': 'color', 'no_create_edit': True}"/>
            </field>
            <notebook position="inside">
                <page string="Travel Information" name="travel_info">
                    <group>
                        <group string="Passport">
                            <field name="passport_image" widget="image" class="oe_avatar"/>
                        </group>
                        <group string="Family Members">
                            <field name="family_member_ids" nolabel="1">
                                <tree editable="bottom">
                                    <field name="name"/>
                                    <field name="phone"/>
                                    <field name="email"/>
                                </tree>
                            </field>
                            <field name="main_contact_id" invisible="1"/>
                        </group>
                    </group>
                </page>
            </notebook>
        </field>
    </record>

    <record id="view_vendor_tree_travel" model="ir.ui.view">
        <field name="name">res.partner.tree.vendor.travel</field>
        <field name="model">res.partner</field>
        <field name="arch" type="xml">
            <tree><field name="name" string="Name"/><field name="phone" string="Phone"/><field name="mobile" string="Mobile"/><field name="email" string="Email"/><field name="service_type_ids" string="Service" widget="many2many_tags"/></tree>
        </field>
    </record>

    <record id="view_financial_summary_tree" model="ir.ui.view">
        <field name="name">res.partner.tree.financial.summary</field>
        <field name="model">res.partner</field>
        <field name="arch" type="xml">
            <tree><field name="display_name" string="Customer"/><field name="sale_order_count_custom" string="Order Count"/><field name="total_sale_value" string="Total Sales" sum="Total Sales"/><field name="total_purchase_value" string="Total Purchase" sum="Total Purchase"/><field name="total_profit_value" string="Total Profit" sum="Total Profit"/><field name="total_receivable" string="Total Receivable"/></tree>
        </field>
    </record>

    <!-- ACTIONS that will be referenced by menus -->
    <record id="action_travel_vendors" model="ir.actions.act_window">
        <field name="name">Vendors</field>
        <field name="res_model">res.partner</field>
        <field name="view_mode">tree,form</field>
        <field name="view_id" ref="view_vendor_tree_travel"/>
        <field name="domain">[('supplier_rank', '>', 0)]</field>
        <field name="context">{'default_is_company': True, 'default_supplier_rank': 1}</field>
    </record>
    <record id="action_travel_customers" model="ir.actions.act_window">
        <field name="name">Customers</field>
        <field name="res_model">res.partner</field>
        <field name="view_mode">tree,form,kanban</field>
        <field name="domain">[('customer_rank', '>', 0)]</field>
        <field name="context">{'default_customer_rank': 1}</field>
    </record>
    <record id="action_travel_financial_summary" model="ir.actions.act_window">
        <field name="name">Financial Report</field>
        <field name="res_model">res.partner</field>
        <field name="view_mode">tree,form</field>
        <field name="view_id" ref="view_financial_summary_tree"/>
        <field name="domain">[('customer_rank', '>', 0)]</field>
    </record>
</odoo>
EOF

cat << 'EOF' > $MODULE_NAME/views/sale_order_views.xml
<odoo>
    <record id="view_order_tree_travel" model="ir.ui.view">
        <field name="name">sale.order.tree.travel</field>
        <field name="model">sale.order</field>
        <field name="arch" type="xml">
            <tree decoration-muted="state == 'cancel'">
                <field name="name" string="Sale ID"/>
                <field name="partner_id" string="Customer"/>
                <field name="date_order" string="Order Date"/>
                <field name="departure_date" string="Departure Date"/>
                <field name="return_date" string="Return Date"/>
                <field name="total_purchase_price" string="Total Purchase" sum="Total"/>
                <field name="total_sale_price" string="Total Sales" sum="Total"/>
                <field name="total_profit" string="Total Profit" sum="Total"/>
                <field name="invoice_status" string="Invoice Status" widget="badge"/>
                <field name="state" string="Status" widget="badge" decoration-success="state == 'sale'" decoration-info="state == 'draft'"/>
            </tree>
        </field>
    </record>

    <record id="view_order_form_travel" model="ir.ui.view">
        <field name="name">sale.order.form.travel</field>
        <field name="model">sale.order</field>
        <field name="inherit_id" ref="sale.view_order_form"/>
        <field name="mode">primary</field>
        <field name="arch" type="xml">
            <!-- The most robust way to replace the form is to replace the whole content of the sheet -->
            <xpath expr="//sheet" position="replace">
                <sheet>
                    <header>
                        <button name="action_confirm" string="Confirm" class="btn-primary" type="object" invisible="state not in ['draft', 'sent']"/>
                        <button name="action_cancel" string="Cancel" type="object" invisible="state not in ['draft', 'sent', 'sale']"/>
                        <field name="state" widget="statusbar" statusbar_visible="draft,sent,sale"/>
                    </header>
                    <h1>
                        <field name="name" readonly="1"/>
                    </h1>
                    <group>
                        <group>
                            <field name="date_order" string="Order Date"/>
                            <field name="departure_date"/>
                            <field name="return_date"/>
                        </group>
                        <group>
                            <field name="partner_id" options="{'no_create': True, 'no_open': True}"/>
                        </group>
                    </group>
                    <group>
                         <group>
                            <field name="from_country_id"/>
                            <field name="from_airport_id" domain="[('country_id', '=', from_country_id)]" options="{'no_create': True}"/>
                        </group>
                         <group>
                            <field name="to_country_id"/>
                            <field name="to_airport_id" domain="[('country_id', '=', to_country_id)]" options="{'no_create': True}"/>
                        </group>
                    </group>
                    <separator string="Family Members and Passports"/>

                    <!-- TICKET SECTION -->
                    <separator string="Ticket"/>
                    <group>
                        <group>
                            <field name="ticket_company_id" options="{'no_create': True}"/>
                            <field name="ticket_purchase_date"/>
                            <field name="ticket_adults"/>
                            <field name="ticket_children"/>
                            <field name="ticket_infants"/>
                        </group>
                        <group>
                            <field name="ticket_number"/>
                            <field name="ticket_note"/>
                        </group>
                    </group>
                    <group string="Ticket Pricing">
                        <group>
                            <field name="ticket_fare"/>
                            <field name="ticket_tax"/>
                            <field name="ticket_purchase_total" string="Purchase Total"/>
                        </group>
                        <group>
                            <field name="ticket_sale_price"/>
                            <label for="ticket_profit_percent"/>
                            <div class="o_row">
                                <field name="ticket_profit_percent"/>
                                <button name="button_calculate_profit_percent" string="Calculate" type="object" class="oe_link"/>
                            </div>
                        </group>
                    </group>

                    <!-- HOTEL SECTION -->
                    <separator string="Hotel"/>
                    <group>
                        <group>
                            <field name="hotel_company_id" options="{'no_create': True}"/>
                            <field name="hotel_room_count"/>
                            <field name="hotel_adults"/>
                            <field name="hotel_children"/>
                            <field name="hotel_infants"/>
                        </group>
                        <group>
                            <label for="hotel_meal_breakfast" string="Meal Plan"/>
                            <div>
                                <field name="hotel_meal_breakfast" class="oe_inline"/><label for="hotel_meal_breakfast" string="Breakfast" class="oe_inline oe_read_only"/>
                                <field name="hotel_meal_lunch" class="oe_inline"/><label for="hotel_meal_lunch" string="Lunch" class="oe_inline oe_read_only"/>
                                <field name="hotel_meal_dinner" class="oe_inline"/><label for="hotel_meal_dinner" string="Dinner" class="oe_inline oe_read_only"/>
                            </div>
                            <field name="hotel_note"/>
                        </group>
                    </group>
                    <group>
                        <group>
                            <field name="hotel_purchase_price"/>
                            <field name="hotel_sale_price"/>
                        </group>
                        <group>
                            <field name="hotel_deadline"/>
                        </group>
                    </group>

                    <!-- OTHER SECTIONS -->
                    <separator string="Transfer"/>
                    <group>
                        <group>
                            <field name="transfer_company_id" options="{'no_create': True}"/>
                            <field name="transfer_type" widget="radio" options="{'horizontal': true}"/>
                            <field name="transfer_from"/>
                            <field name="transfer_to"/>
                        </group>
                        <group>
                            <field name="transfer_datetime"/>
                            <field name="transfer_deadline"/>
                            <field name="transfer_note"/>
                        </group>
                    </group>
                    <group>
                        <field name="transfer_purchase_price"/><field name="transfer_sale_price"/>
                    </group>

                    <separator string="Insurance"/>
                    <group>
                        <group><field name="insurance_company_id" options="{'no_create': True}"/><field name="insurance_country_id"/><field name="insurance_date"/></group>
                        <group><field name="insurance_note"/></group>
                    </group>
                    <group><field name="insurance_purchase_price"/><field name="insurance_sale_price"/></group>

                    <separator string="Tour Package"/>
                    <group>
                        <group><field name="tour_package_id"/><field name="tour_company_id" options="{'no_create': True}"/></group>
                        <group><field name="tour_deadline"/><field name="tour_note"/></group>
                    </group>
                    <group><field name="tour_purchase_price"/><field name="tour_sale_price"/></group>

                    <separator string="Visa"/>
                    <group>
                        <group><field name="visa_company_id" options="{'no_create': True}"/></group>
                        <group><field name="visa_note"/></group>
                    </group>
                     <group><field name="visa_purchase_price"/><field name="visa_sale_price"/></group>

                    <separator string="Other"/>
                    <group>
                        <group><field name="other_service_name"/></group>
                        <group><field name="other_note"/></group>
                    </group>
                     <group><field name="other_purchase_price"/><field name="other_sale_price"/></group>
                    
                    <!-- Totals Section -->
                    <group class="oe_subtotal_footer oe_right" style="margin-top: 20px;">
                        <field name="total_purchase_price"/>
                        <field name="total_sale_price"/>
                        <field name="total_profit" class="oe_subtotal_footer_separator"/>
                    </group>
                </sheet>
            </xpath>
        </field>
    </record>
    
    <!-- ACTION for sales -->
    <record id="action_travel_sale_orders" model="ir.actions.act_window">
        <field name="name">Sales</field>
        <field name="type">ir.actions.act_window</field>
        <field name="res_model">sale.order</field>
        <field name="view_mode">tree,form,calendar,graph</field>
        <field name="view_id" ref="view_order_tree_travel"/>
        <field name="help" type="html"><p class="o_view_nocontent_smiling_face">Create a new sales order!</p></field>
    </record>
</odoo>
EOF

cat << 'EOF' > $MODULE_NAME/views/main_menus.xml
<odoo>
    <!-- Main Root Menu -->
    <menuitem id="travel_agency_root_menu" name="Travel Agency" web_icon="travel_agency_management,static/description/icon.svg" sequence="1"/>

    <!-- Menu Items -->
    <menuitem id="travel_sale_orders_menu" name="Sales" parent="travel_agency_root_menu" action="travel_agency_management.action_travel_sale_orders" sequence="10"/>
    <menuitem id="travel_vendors_menu" name="Vendors" parent="travel_agency_root_menu" action="travel_agency_management.action_travel_vendors" sequence="20"/>
    <menuitem id="travel_customers_menu" name="Customers" parent="travel_agency_root_menu" action="travel_agency_management.action_travel_customers" sequence="30"/>
    <menuitem id="travel_finance_menu" name="Finance" parent="travel_agency_root_menu" action="travel_agency_management.action_travel_financial_summary" sequence="40"/>
    
    <record id="action_travel_bank_payments" model="ir.actions.act_window">
        <field name="name">Bank Payments</field><field name="res_model">account.payment</field><field name="view_mode">tree,form,graph</field>
        <field name="domain">[('journal_id.type', '=', 'bank')]</field>
        <field name="context">{'default_journal_id': ref('account.account_journal_bank', raise_if_not_found=False), 'default_payment_type': 'inbound'}</field>
    </record>
    <menuitem id="travel_bank_menu" name="Bank" parent="travel_agency_root_menu" action="action_travel_bank_payments" sequence="50"/>
    
    <record id="action_travel_cash_payments" model="ir.actions.act_window">
        <field name="name">Cash Payments</field><field name="res_model">account.payment</field><field name="view_mode">tree,form,graph</field>
        <field name="domain">[('journal_id.type', '=', 'cash')]</field>
        <field name="context">{'default_journal_id': ref('account.account_journal_cash', raise_if_not_found=False), 'default_payment_type': 'inbound'}</field>
    </record>
    <menuitem id="travel_cash_menu" name="Cash" parent="travel_agency_root_menu" action="action_travel_cash_payments" sequence="60"/>

    <!-- CONFIGURATION SUB-MENU -->
    <menuitem id="travel_configuration_menu" name="Configuration" parent="travel_agency_root_menu" sequence="100"/>
    <record id="action_travel_airports" model="ir.actions.act_window">
        <field name="name">Airports</field><field name="res_model">travel.airport</field><field name="view_mode">tree,form</field>
    </record>
    <menuitem id="travel_airports_menu" name="Airports" parent="travel_configuration_menu" action="action_travel_airports" sequence="10"/>
</odoo>
EOF


# 7. Create the static icon file
echo "-> Creating SVG icon for the menu..."
cat << 'EOF' > $MODULE_NAME/static/description/icon.svg
<svg id="Layer_1" enable-background="new 0 0 512 512" height="88px" viewBox="0 0 512 512" width="88px" xmlns="http://www.w3.org/2000/svg"><g><path d="m497 101v330c0 11.028-8.972 20-20 20h-35v-101h-30v101h-312v-101h-30v101h-35c-11.028 0-20-8.972-20-20v-330c0-11.028 8.972-20 20-20h422c11.028 0 20 8.972 20 20zm-20 0h-422v20h422z" fill="#757575"/><path d="m156 320h200c8.284 0 15-6.716 15-15v-190c0-8.284-6.716-15-15-15h-200c-8.284 0-15 6.716-15 15v190c0 8.284 6.716 15 15 15z" fill="#9e9e9e"/><path d="m371 190h30v60h-30z" fill="#757575"/><path d="m111 190h30v60h-30z" fill="#757575"/><g><path d="m311 250h30v-120h-30z" fill="#616161"/><path d="m241 250h30v-120h-30z" fill="#616161"/><path d="m171 250h30v-120h-30z" fill="#616161"/></g></g></svg>
EOF


echo ""
echo "========================================================================"
echo "    Module '$MODULE_NAME' (English, Rev 1.5) created successfully!      "
echo "                  (Fixed XPath location error)                          "
echo "========================================================================"
echo ""
echo "Next Steps:"
echo "1. Restart your Odoo service."
echo "2. Activate Developer Mode in the Odoo UI."
echo "3. Go to the 'Apps' menu and click 'Update Apps List'."
echo "4. Search for '$MODULE_NAME' and click 'Upgrade'."
echo ""

exit 0