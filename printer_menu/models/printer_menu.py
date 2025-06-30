from odoo import tools, fields, models, api,_
from odoo.exceptions import UserError
from odoo.exceptions import ValidationError
import requests
import json
import subprocess
from datetime import datetime
from base64 import b64encode
from escpos.printer import Usb
 

cookie = "printer_menu"

 
 
 

class PrinterMenuProfile(models.Model):
    
    _name = "printer_menu.profile"
    _description = "Printer Menu Profile"
    

    name = fields.Char(string="Printer Name", required=True)
    sequence = fields.Char(string="sequence")
    vendor_id = fields.Char(string="Vendor ID", required=True)
    product_id = fields.Char(string="Product ID", required=True)
    
    description = fields.Text(string='Description')
    create_date = fields.Datetime(string='Created Date', default=fields.Datetime.now)
    
    def _get_report_values(self, docids, data=None):
        docs = self.env['printer_menu.profile'].browse(docids)
        return {
            'doc_ids': docids,
            'doc_model': 'printer.menu.profile',
            'docs': docs,
        }

    def action_test_print(self):
        
        raise UserError("Test print executed successfully.")
    
    @api.model
    def print_receipt(self, sale_order_id):
        sale_order = self.env['sale.order'].browse(sale_order_id)
        if not sale_order:
            raise UserError(_("Sale Order not found."))

        # Yazıcıyı bağla
        try:
            vendor_id = int(self.vendor_id, 16)
            product_id = int(self.product_id, 16)
            printer = Usb(vendor_id, product_id)
        except Exception as e:
            raise UserError(_("Printer connection failed: %s" % str(e)))

        # Yazıcıya fiş yazdır
        try:
            tarih = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
            printer.text("FIŞ BAŞLIĞI\n".encode('utf-8'))
            printer.text(f"Tarih: {tarih}\n".encode('utf-8'))
            printer.text("-" * 32 + "\n".encode('utf-8'))
            for line in sale_order.order_line:
                product_name = line.product_id.name[:20]
                qty = line.product_uom_qty
                price = line.price_unit
                printer.text(f"{product_name:<20}{qty:<4}{price:>8.2f}₺\n".encode('utf-8'))
            printer.text("-" * 32 + "\n".encode('utf-8'))
            printer.text(f"Toplam: {sale_order.amount_total:.2f}₺\n".encode('utf-8'))
            printer.text("Teşekkürler!\n".encode('utf-8'))
            printer.cut()
        except Exception as e:
            raise UserError(_("Printing failed: %s" % str(e)))
    

 

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    printed = fields.Boolean(string="Printed", default=False)
    
    def action_print_order_receipt(self):
        """
        Sipariş PDF'ini oluştur ve yazıcıya gönder.
        """
        self.ensure_one()  # Tek bir kayıt üzerinde çalışıldığından emin olun
        pdf_content, _ = self.env['ir.actions.report']._render_qweb_pdf(
            'sale.report_saleorder', res_ids=[self.id]
        )
        pdf_path = f"/tmp/sale_order_{self.id}.pdf"
        try:
            with open(pdf_path, 'wb') as pdf_file:
                pdf_file.write(pdf_content)
        except Exception as e:
            raise ValueError(_("Error while saving PDF: %s") % str(e))

        # Yazıcıya gönderme
        try:
            conn = cups.Connection()
            printers = conn.getPrinters()
            default_printer = conn.getDefault()
            if not default_printer:
                raise ValueError(_("Default printer not configured."))
            conn.printFile(default_printer, pdf_path, f"Order {self.name}", {})
        except cups.CUPSException as e:
            raise UserError(_("CUPS Error: %s") % str(e))
        except Exception as e:
            raise UserError(_("Printing failed: %s") % str(e))
    
    """ def action_print_order_receipt(self):
        
        
        # Sipariş PDF'ini oluştur ve yazıcıya gönder.
      
        self.ensure_one()  # Tek bir kayıt üzerinde çalışıldığından emin olun
        pdf_content, _ = self.env['ir.actions.report']._render_qweb_pdf(
            'sale.report_saleorder', res_ids=[self.id]
        )
        pdf_path = f"/tmp/sale_order_{self.id}.pdf"
        with open(pdf_path, 'wb') as pdf_file:
            pdf_file.write(pdf_content)

        # Yazıcıya gönderme
        try:
            conn = cups.Connection()
            printers = conn.getPrinters()
            default_printer = conn.getDefault()
            if not default_printer:
                raise ValueError("Default printer not configured.")
            conn.printFile(default_printer, pdf_path, f"Order {self.name}", {})
        except Exception as e:
            raise ValueError(_("Printing failed: %s") % str(e)) """
    
       
    """ def action_generate_receipt(self):
        # PDF'i oluştur ve döndür
        return self.env.ref('printer_menu.receipt_report').report_action(self) """
    
    """ def action_generate_receipt(self):
        # PDF içeriği oluşturma
        pdf_content = pdf.PDFGenerator().render(
            'printer_menu.receipt_template',  # QWeb template ID
            {'sale_order': self}
        )

        # PDF'i döndür
        return {
            'type': 'ir.actions.report',
            'report_type': 'qweb-pdf',
            'data': pdf_content,
        } """

    """ def action_print_receipt(self):
        # İlk termal yazıcıyı al
        thermal_printer = self.env['printer_menu.profile'].search([], limit=1)
        if not thermal_printer:
            raise UserError(_("No thermal printer configured. Please configure a printer in settings."))

        # Fiş yazdır
        thermal_printer.print_receipt(self.id) """
    
    """ @api.model
    def create(self, vals):
        # Yeni bir sipariş oluşturulduğunda çalışır
        order = super(SaleOrder, self).create(vals)
        order.send_to_printer()  # Yazdırma işlemini çağır
        return order

    def write(self, vals):
        # Sipariş güncellendiğinde çalışır
        res = super(SaleOrder, self).write(vals)
        if 'state' in vals and vals['state'] == 'sale':  # Satış onaylandığında yazdır
            self.send_to_printer()
        return res """


    '''
    def send_to_printer(self):
        # Yazdırma işlemini başlat
        report = self.env.ref('printer_menu.report_order_action')._render_qweb_pdf(self.id)
        pdf_content = report[0]
        with open('/tmp/order_report.pdf', 'wb') as f:
            f.write(pdf_content)

        # Yazıcıya gönder (ör. lp veya CUPS)
        
        subprocess.run(["lp", "/tmp/order_report.pdf"])'''
                              
class ResPartnersInherit(models.Model):
    _inherit = 'res.partner'
 
 