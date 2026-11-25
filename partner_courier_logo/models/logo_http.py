import socket
from http.client import HTTPSConnection
from urllib.request import HTTPSHandler


def create_ipv4_connection(address, timeout=socket._GLOBAL_DEFAULT_TIMEOUT, source_address=None):
    """Resolve Logo over IPv4 while leaving other Odoo connections untouched."""
    addresses = socket.getaddrinfo(address[0], address[1], socket.AF_INET, socket.SOCK_STREAM)
    last_error = None
    for _family, _socktype, _proto, _canonname, sockaddr in addresses:
        try:
            return socket.create_connection(sockaddr, timeout, source_address)
        except OSError as exc:
            last_error = exc
    if last_error is not None:
        raise last_error
    raise OSError('No IPv4 address found for Logo API host')


class LogoIPv4HTTPSConnection(HTTPSConnection):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Keep the original hostname for TLS certificate checks, SNI and Host.
        self._create_connection = create_ipv4_connection


class LogoIPv4HTTPSHandler(HTTPSHandler):

    def https_open(self, request):
        return self.do_open(LogoIPv4HTTPSConnection, request, context=self._context)
