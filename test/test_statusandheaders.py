"""
>>> st1 = StatusAndHeadersParser(['HTTP/1.0']).parse(StringIO(status_headers_1))
>>> st1
StatusAndHeaders(protocol = 'HTTP/1.0', statusline = '200 OK', headers = [('Content-Type', 'ABC'), ('Some', 'Value'), ('Multi-Line', 'Value1    Also This')])

# add range (and byte headers)
>>> StatusAndHeaders(statusline = '200 OK', headers=[(b'Content-Type', b'text/plain')]).add_range(10, 4, 100)
StatusAndHeaders(protocol = '', statusline = '206 Partial Content', headers = [('Content-Type', 'text/plain'), ('Content-Range', 'bytes 10-13/100'), ('Accept-Ranges', 'bytes')])

# other protocol expected
>>> StatusAndHeadersParser(['Other']).parse(StringIO(status_headers_1))  # doctest: +IGNORE_EXCEPTION_DETAIL
Traceback (most recent call last):
StatusAndHeadersParserException: Expected Status Line starting with ['Other'] - Found: HTTP/1.0 200 OK

>>> StatusAndHeadersParser(['Other'], verify=False).parse(StringIO(status_headers_1))
StatusAndHeaders(protocol = 'HTTP/1.0', statusline = '200 OK', headers = [('Content-Type', 'ABC'), ('Some', 'Value'), ('Multi-Line', 'Value1    Also This')])


# verify protocol line
>>> StatusAndHeadersParser(['HTTP/1.0'], verify=True).parse(StringIO(unknown_protocol_headers))  # doctest: +IGNORE_EXCEPTION_DETAIL
Traceback (most recent call last):
StatusAndHeadersParserException: Expected Status Line starting with ['HTTP/1.0'] - Found: OtherBlah


# allow unexpected/invalid protocol line
>>> StatusAndHeadersParser(['HTTP/1.0'], verify=False).parse(StringIO(unknown_protocol_headers))
StatusAndHeaders(protocol = 'OtherBlah', statusline = '', headers = [('Foo', 'Bar')])



# test equality op
>>> st1 == StatusAndHeadersParser(['HTTP/1.0']).parse(StringIO(status_headers_1))
True

# replace header, print new headers
>>> st1.replace_header('some', 'Another-Value'); st1
'Value'
StatusAndHeaders(protocol = 'HTTP/1.0', statusline = '200 OK', headers = [('Content-Type', 'ABC'), ('Some', 'Another-Value'), ('Multi-Line', 'Value1    Also This')])


# replace header with dict-like api, print new headers
>>> st1['some'] = 'Yet-Another-Value'; st1
StatusAndHeaders(protocol = 'HTTP/1.0', statusline = '200 OK', headers = [('Content-Type', 'ABC'), ('Some', 'Yet-Another-Value'), ('Multi-Line', 'Value1    Also This')])


# remove header
>>> st1.remove_header('some')
True

# already removed
>>> st1.remove_header('Some')
False

# add header with dict-like api, print new headers
>>> st1['foo'] = 'bar'; st1
StatusAndHeaders(protocol = 'HTTP/1.0', statusline = '200 OK', headers = [('Content-Type', 'ABC'), ('Multi-Line', 'Value1    Also This'), ('foo', 'bar')])

# dict-like api existence and get value
>>> 'bar' in st1
False
>>> 'foo' in st1
True
>>> st1['bar']
>>> st1.get('bar')
>>> st1['foo']
'bar'
>>> st1.get('foo')
'bar'

# remove header with dict-like api, print new headers
>>> del st1['foo']; st1
StatusAndHeaders(protocol = 'HTTP/1.0', statusline = '200 OK', headers = [('Content-Type', 'ABC'), ('Multi-Line', 'Value1    Also This')])

# empty
>>> st2 = StatusAndHeadersParser(['HTTP/1.0']).parse(StringIO(status_headers_2)); x = st2.validate_statusline('204 No Content'); st2
StatusAndHeaders(protocol = '', statusline = '204 No Content', headers = [])


>>> StatusAndHeadersParser(['HTTP/1.0']).parse(StringIO(status_headers_3))
StatusAndHeaders(protocol = 'HTTP/1.0', statusline = '204 Empty', headers = [('Content-Type', 'Value'), ('Content-Length', '0')])

# case-insensitive match
>>> StatusAndHeadersParser(['HTTP/1.0']).parse(StringIO(status_headers_4))
StatusAndHeaders(protocol = 'HTTP/1.0', statusline = '204 empty', headers = [('Content-Type', 'Value'), ('Content-Length', '0')])


"""


from warcio.statusandheaders import StatusAndHeadersParser, StatusAndHeaders
from six import StringIO
import pytest


status_headers_1 = "\
HTTP/1.0 200 OK\r\n\
Content-Type: ABC\r\n\
HTTP/1.0 200 OK\r\n\
Some: Value\r\n\
Multi-Line: Value1\r\n\
    Also This\r\n\
\r\n\
Body"


status_headers_2 = """

"""

status_headers_3 = "\
HTTP/1.0 204 Empty\r\n\
Content-Type: Value\r\n\
%Invalid%\r\n\
\tMultiline\r\n\
Content-Length: 0\r\n\
\r\n"

status_headers_4 = "\
http/1.0 204 empty\r\n\
Content-Type: Value\r\n\
%Invalid%\r\n\
\tMultiline\r\n\
Content-Length: 0\r\n\
\r\n"

unknown_protocol_headers = "\
OtherBlah\r\n\
Foo: Bar\r\n\
\r\n"


req_headers = "\
GET / HTTP/1.0\r\n\
Foo: Bar\r\n\
Content-Length: 0\r\n"


if __name__ == "__main__":
    import doctest
    doctest.testmod()



def test_to_str_1():
    res = str(StatusAndHeadersParser(['HTTP/1.0']).parse(StringIO(status_headers_1)))

    exp = "\
HTTP/1.0 200 OK\r\n\
Content-Type: ABC\r\n\
Some: Value\r\n\
Multi-Line: Value1    Also This\r\n\
"
    assert(res == exp)


def test_to_str_exclude():
    def exclude(h):
        if h[0].lower() == 'multi-line':
            return None

        return h

    sah = StatusAndHeadersParser(['HTTP/1.0']).parse(StringIO(status_headers_1))
    res = sah.to_str(exclude)

    exp = "\
HTTP/1.0 200 OK\r\n\
Content-Type: ABC\r\n\
Some: Value\r\n\
"
    assert(res == exp)

    assert(sah.to_bytes(exclude) == (exp.encode('latin-1') + b'\r\n'))


def test_to_str_2():
    res = str(StatusAndHeadersParser(['GET']).parse(StringIO(req_headers)))

    assert(res == req_headers)

    res = str(StatusAndHeadersParser(['GET']).parse(StringIO(req_headers + '\r\n')))

    assert(res == req_headers)


def test_to_str_with_remove():
    res = StatusAndHeadersParser(['GET']).parse(StringIO(req_headers))
    res.remove_header('Foo')

    exp = "\
GET / HTTP/1.0\r\n\
Content-Length: 0\r\n"

    assert(str(res) == exp)


def test_status_empty():
    with pytest.raises(EOFError):
        StatusAndHeadersParser([], verify=False).parse(StringIO(''))


def test_status_one_word():
    res = StatusAndHeadersParser(['GET'], verify=False).parse(StringIO('A'))
    assert(str(res) == 'A\r\n')

def test_validate_status():
    assert StatusAndHeaders('200 OK', []).validate_statusline('204 No Content')
    assert not StatusAndHeaders('Bad OK', []).validate_statusline('204 No Content')


