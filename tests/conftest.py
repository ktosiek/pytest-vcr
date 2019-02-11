import pytest
from threading import Thread
try:
    from http.server import HTTPServer, BaseHTTPRequestHandler
except ImportError:
    from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler

pytest_plugins = 'pytester'


@pytest.fixture(scope='session')
def live_server():
    return LiveServer()


class LiveServer(object):
    def __init__(self):
        self.server = HTTPServer(('127.0.0.1', 0), TestHTTPHandler)
        self.thread = Thread(None, self.server.serve_forever)
        self.thread.daemon = True
        self.thread.start()

    @property
    def address(self):
        sockname = self.server.socket.getsockname()
        return 'http://' + sockname[0] + ':' + str(sockname[1]) + '/'


class TestHTTPHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        response = ('Example domains ' * 10).encode('ascii')

        self.send_response(200)
        self.send_header("Content-Type", "text/html")
        self.send_header("Content-Length", str(len(response)))
        self.end_headers()
        self.wfile.write(response)
