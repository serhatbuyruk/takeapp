# -*- coding: utf-8 -*-
#############################################################################
#
#    Cybrosys Technologies Pvt. Ltd.
#
#    Copyright (C) 2023-TODAY Cybrosys Technologies(<https://www.cybrosys.com>)
#    Author: Cybrosys Techno Solutions(<https://www.cybrosys.com>)
#
#    This program is free software: you can modify
#    it under the terms of the GNU Affero General Public License (AGPL) as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
#############################################################################
import base64
import io
import xlsxwriter
from io import BytesIO
from odoo import http
from odoo.http import content_disposition, request
from odoo.tools import image_process


class ExcelReportController(http.Controller):
    """
    This class includes the function to downloads excel report.
    """

    @http.route(
        [
            '/products_download/excel_report/<model("product.export"):wizards>',
        ],
        type="http",
        auth="public",
        csrf=False,
    )
    def get_product_excel_report(self, wizards=None):
        """
        Downloads the Excel document with the details of products
        """
        response = request.make_response(
            None,
            headers=[
                ("Content-Type", "application/vnd.ms-excel"),
                ("Content-Disposition", content_disposition("Products" + ".xlsx")),
            ],
        )
        # create workbook object from xlsxwriter library
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {"in_memory": True})
        # create styles to set up the font type, the font size, the border,
        # and the alignment
        header_style = workbook.add_format(
            {
                "text_wrap": True,
                "font_name": "Times",
                "bold": True,
                "left": 1,
                "bottom": 1,
                "right": 1,
                "top": 1,
                "align": "center",
            }
        )
        text_style = workbook.add_format(
            {
                "text_wrap": True,
                "font_name": "Times",
                "left": 1,
                "bottom": 1,
                "right": 1,
                "top": 1,
                "align": "left",
            }
        )
        product_lines = wizards.get_product_lines()
        sheet = workbook.add_worksheet("Products")
        sheet.set_landscape()
        sheet.set_paper(9)
        sheet.merge_range("A1:G1", "OPERASYONEL UYGUNSUZLUK TAKİP RAPORU", header_style)
        sheet.set_margins(0.5, 0.5, 0.5, 0.5)
        sheet.set_column("A:A", 10)
        sheet.set_column("B:C", 15)
        sheet.set_column("D:D", 20)
        sheet.set_column("E:E", 35)
        sheet.set_column("F:F", 15)
        sheet.set_column("G:G", 15)
        sheet.set_column("H:H", 17)
        sheet.set_column("I:I", 17)
        sheet.set_row(1, 30)
        sheet.set_row(0, 30)
        # table title
        sheet.write(2, 0, "TARİH", header_style)
        sheet.write(2, 1, "DENETLENEN BÖLGE", header_style)
        sheet.write(2, 2, "İLGİLİ DEPARTMAN", header_style)
        sheet.write(2, 3, "TESPİT EDİLEN UYGUNSUZLUK", header_style)
        # sheet.write(2, 4, "TESPİT EDİLEN UYGUNSUZLUK-2", header_style)
        sheet.write(2, 4, "AÇIKLAMA", header_style)
        sheet.write(2, 5, "AKSİYON", header_style)
        sheet.write(2, 6, "TERMİN TARİHİ", header_style)
        sheet.write(2, 7, "UYGUNSUZLUK SON DURUMU", header_style)
        sheet.write(2, 8, "İLGİLİ DEPARTMANIN AÇIKLAMASI", header_style)
        row = 3
        number = 1
        count = 0
        for line in product_lines:
            sheet.set_row(row, 128)
            # the report content
            count += 1
            sheet.write(row, 0, count, text_style)
            if line["x_tarih"]:
                sheet.write(row, 0, line["x_tarih"], text_style)
            elif not line["x_tarih"]:
                sheet.write(row, 0, "", text_style)
            sheet.write(row, 1, line["name"], text_style)
            sheet.write(row, 2, line["category"], text_style)
            if line["image"]:
                source = base64.b64decode(line["image"])
                image_data = BytesIO(image_process(source, size=(150, 150)))
                sheet.write(row, 3, "", text_style)
                sheet.insert_image(row, 3, "product.png", {"image_data": image_data})
            sheet.write(row, 4, line["description"].replace("<p>","").replace("</p>",""), text_style)
            sheet.write(row, 5, line["x_aksiyon"], text_style)
            sheet.write(row, 6, line["x_termin_tarihi"], text_style)
            sheet.write(row, 7, line["x_uygunsuzluk_son_durum"], text_style)
            if line["x_ilgili_departman_aciklamasi"]:
                sheet.write(row, 8, line["x_ilgili_departman_aciklamasi"], text_style)
            elif not line["x_ilgili_departman_aciklamasi"]:
                sheet.write(row, 8, "", text_style)      
            row += 1
            number += 1
        workbook.close()
        output.seek(0)
        response.stream.write(output.read())
        output.close()
        return response
