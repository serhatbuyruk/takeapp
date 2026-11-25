from odoo.tests.common import TransactionCase


class TestPartnerCourierLogoHttpError(TransactionCase):

    def test_cloudflare_html_is_replaced_with_safe_message_and_reference(self):
        detail = '''
            <!DOCTYPE html>
            <title>Attention Required! | Cloudflare</title>
            <h1>Sorry, you have been blocked</h1>
            <span>Cloudflare Ray ID:</span>
            <strong>a593fb652808dc79</strong>
        '''

        message = self.env['partner.courier.logo.invoice']._http_error_detail(403, detail)

        self.assertNotIn('<!DOCTYPE', message)
        self.assertNotIn('<title>', message)
        self.assertIn('Fatura oluşturulmadı', message)
        self.assertIn('a593fb652808dc79', message)

    def test_regular_api_error_is_kept(self):
        detail = '{"message":"Geçersiz oturum anahtarı"}'

        message = self.env['partner.courier.logo.invoice']._http_error_detail(401, detail)

        self.assertEqual(message, detail)
