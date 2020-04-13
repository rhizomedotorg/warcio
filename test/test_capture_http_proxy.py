from warcio.capture_http import capture_http

import threading
from wsgiref.simple_server import make_server
import time

import requests
from warcio.archiveiterator import ArchiveIterator

from pytest import raises


# ==================================================================
class TestCaptureHttpProxy():
    @classmethod
    def setup_class(cls):
        def app(env, start_response):
            result = ('Proxied: ' + env['PATH_INFO']).encode('utf-8')
            headers = [('Content-Length', str(len(result)))]
            start_response('200 OK', headers=headers)
            return iter([result])

        from wsgiprox.wsgiprox import WSGIProxMiddleware
        wsgiprox = WSGIProxMiddleware(app, '/')

        server = make_server('localhost', 0, wsgiprox)
        addr, cls.port = server.socket.getsockname()

        cls.proxies = {'https': 'localhost:' + str(cls.port),
                       'http': 'localhost:' + str(cls.port)
                      }

        def run():
            try:
                server.serve_forever()
            except  Exception as e:
                print(e)

        thread = threading.Thread(target=run)
        thread.daemon = True
        thread.start()
        time.sleep(0.1)

    def test_capture_http_proxy(self):
        with capture_http() as warc_writer:
            res = requests.get("http://example.com/test", proxies=self.proxies, verify=False)

        ai = ArchiveIterator(warc_writer.get_stream())
        response = next(ai)
        assert response.rec_type == 'response'
        assert response.rec_headers['WARC-Target-URI'] == "http://example.com/test"
        assert response.content_stream().read().decode('utf-8') == 'Proxied: /http://example.com/test'

        request = next(ai)
        assert request.rec_type == 'request'
        assert request.rec_headers['WARC-Target-URI'] == "http://example.com/test"

        with raises(StopIteration):
            assert next(ai)

    def test_capture_https_proxy(self):
        with capture_http() as warc_writer:
            res = requests.get("https://example.com/test", proxies=self.proxies, verify=False)
            res = requests.get("https://example.com/foo", proxies=self.proxies, verify=False)

        ai = ArchiveIterator(warc_writer.get_stream())
        response = next(ai)
        assert response.rec_type == 'response'
        assert response.rec_headers['WARC-Target-URI'] == "https://example.com/test"
        assert response.content_stream().read().decode('utf-8') == 'Proxied: /https://example.com/test'

        request = next(ai)
        assert request.rec_type == 'request'
        assert request.rec_headers['WARC-Target-URI'] == "https://example.com/test"

        response = next(ai)
        assert response.rec_type == 'response'
        assert response.rec_headers['WARC-Target-URI'] == "https://example.com/foo"
        assert response.content_stream().read().decode('utf-8') == 'Proxied: /https://example.com/foo'

        request = next(ai)
        assert request.rec_type == 'request'
        assert request.rec_headers['WARC-Target-URI'] == "https://example.com/foo"

        with raises(StopIteration):
            assert next(ai)

    def test_capture_https_proxy_same_session(self):
        sesh = requests.session()
        with capture_http() as warc_writer:
            res = sesh.get("https://example.com/test", proxies=self.proxies, verify=False)
            res = sesh.get("https://example.com/foo", proxies=self.proxies, verify=False)

        ai = ArchiveIterator(warc_writer.get_stream())
        response = next(ai)
        assert response.rec_type == 'response'
        assert response.rec_headers['WARC-Target-URI'] == "https://example.com/test"
        assert response.content_stream().read().decode('utf-8') == 'Proxied: /https://example.com/test'

        request = next(ai)
        assert request.rec_type == 'request'
        assert request.rec_headers['WARC-Target-URI'] == "https://example.com/test"

        response = next(ai)
        assert response.rec_type == 'response'
        assert response.rec_headers['WARC-Target-URI'] == "https://example.com/foo"
        assert response.content_stream().read().decode('utf-8') == 'Proxied: /https://example.com/foo'

        request = next(ai)
        assert request.rec_type == 'request'
        assert request.rec_headers['WARC-Target-URI'] == "https://example.com/foo"

        with raises(StopIteration):
            assert next(ai)

