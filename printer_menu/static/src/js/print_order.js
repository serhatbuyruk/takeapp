odoo.define('sale_order.print_order', function (require) {
    "use strict";

    $(document).on('click', '#print-order-btn', function () {
        const orderId = $(this).data('order-id');
        const pdfUrl = `/sale/order/${orderId}/print`;
        const iframe = document.createElement('iframe');
        iframe.style.display = 'none';
        iframe.src = pdfUrl;
        document.body.appendChild(iframe);
        iframe.onload = function () {
            iframe.contentWindow.print();
            document.body.removeChild(iframe);
        };
    });
});