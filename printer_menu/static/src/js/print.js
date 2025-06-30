odoo.define('printer_menu.print_receipt', function (require) {
    "use strict";

    // Print PDF Function
    function printPDF(pdfUrl) {
        const iframe = document.createElement('iframe');
        iframe.style.display = 'none';
        iframe.src = pdfUrl;
        document.body.appendChild(iframe);
        iframe.onload = function () {
            iframe.contentWindow.print();
            document.body.removeChild(iframe);
        };
    }

    // Expose to global scope if needed
    return {
        printPDF,
    };
});
