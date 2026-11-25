import socket
import ssl
from unittest.mock import Mock, patch

from odoo.tests.common import BaseCase

from ..models import logo_http


class TestLogoIPv4Transport(BaseCase):

    def test_resolves_only_ipv4_and_keeps_timeout(self):
        address = ('integration.isbasi.com', 443)
        resolved = (socket.AF_INET, socket.SOCK_STREAM, 6, '', ('192.0.2.10', 443))
        expected_socket = Mock()
        with patch.object(logo_http.socket, 'getaddrinfo', return_value=[resolved]) as resolve, \
                patch.object(logo_http.socket, 'create_connection', return_value=expected_socket) as connect:
            result = logo_http.create_ipv4_connection(address, timeout=30)

        resolve.assert_called_once_with(address[0], address[1], socket.AF_INET, socket.SOCK_STREAM)
        connect.assert_called_once_with(('192.0.2.10', 443), 30, None)
        self.assertIs(result, expected_socket)

    def test_tries_next_ipv4_address_after_connection_failure(self):
        resolved = [
            (socket.AF_INET, socket.SOCK_STREAM, 6, '', ('192.0.2.10', 443)),
            (socket.AF_INET, socket.SOCK_STREAM, 6, '', ('192.0.2.11', 443)),
        ]
        expected_socket = Mock()
        with patch.object(logo_http.socket, 'getaddrinfo', return_value=resolved), \
                patch.object(logo_http.socket, 'create_connection', side_effect=[OSError('unreachable'), expected_socket]) as connect:
            result = logo_http.create_ipv4_connection(('integration.isbasi.com', 443), timeout=30)

        self.assertEqual(connect.call_count, 2)
        self.assertIs(result, expected_socket)

    def test_all_ipv4_failures_are_reported(self):
        resolved = [(socket.AF_INET, socket.SOCK_STREAM, 6, '', ('192.0.2.10', 443))]
        with patch.object(logo_http.socket, 'getaddrinfo', return_value=resolved), \
                patch.object(logo_http.socket, 'create_connection', side_effect=OSError('unreachable')):
            with self.assertRaisesRegex(OSError, 'unreachable'):
                logo_http.create_ipv4_connection(('integration.isbasi.com', 443), timeout=30)

    def test_original_hostname_and_tls_verification_are_preserved(self):
        original_connect = socket.create_connection
        connection = logo_http.LogoIPv4HTTPSConnection('integration.isbasi.com', timeout=30)

        self.assertEqual(connection.host, 'integration.isbasi.com')
        self.assertTrue(connection._context.check_hostname)
        self.assertEqual(connection._context.verify_mode, ssl.CERT_REQUIRED)
        self.assertIs(connection._create_connection, logo_http.create_ipv4_connection)
        self.assertIs(socket.create_connection, original_connect)
