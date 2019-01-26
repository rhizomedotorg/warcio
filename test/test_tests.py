from warcio.cli import main

from . import get_test_file
from .test_cli import patch_stdout
from warcio.utils import to_native_str


def helper(args, expected_exit_value):
    with patch_stdout() as buff:
        exit_value = None
        try:
            main(args=args)
        except SystemExit as e:
            exit_value = e.code
        finally:
            assert exit_value == expected_exit_value

        return to_native_str(buff.getvalue())


def remove_before_test_data(s):
    ret = ''
    for line in s.splitlines(True):
        if '/test/data/' in line:
            line = 'test/data/' + line.split('/test/data/', 1)[1]
        ret += line
    return ret


def test_torture_missing():
    files = ['standard-torture-missing.warc']
    files = [get_test_file(filename) for filename in files]

    args = ['test']
    args.extend(files)

    expected = """\
test/data/standard-torture-missing.warc
  WARC-Record-ID None
    WARC-Type warcinfo
    digest not present
    error: missing required header Content-Type
    error: missing required header WARC-Date
    error: missing required header WARC-Record-ID
    recommendation: warcinfo Content-Type of application/warc-fields, saw none
"""

    value = helper(args, 0)
    assert remove_before_test_data(value) == expected


def test_torture_validate_record():
    files = ['standard-torture-validate-record.warc']
    files = [get_test_file(filename) for filename in files]

    args = ['test']
    args.extend(files)

    expected = """\
test/data/standard-torture-validate-record.warc
  WARC-Record-ID None
    WARC-Type warcinfo
    digest not present
    error: missing required header WARC-Date
    error: missing required header WARC-Record-ID
    error: warc-fields contains invalid utf-8: 'utf-8' codec can't decode byte 0xc3 in position 57: invalid continuation byte
    comment: The first line of warc-fields cannot start with whitespace
    comment: warc-fields lines must end with \\r\\n: test: lines should end with \\r\\n
    comment: Missing field-name : in warc-fields line: no colon
    comment: invalid warc-fields name: token cannot have a space
  WARC-Record-ID None
    WARC-Type warcinfo
    digest not present
    error: missing required header WARC-Date
    error: missing required header WARC-Record-ID
    comment: warc-fields body present but empty
  WARC-Record-ID None
    WARC-Type response
    digest not present
    error: missing required header WARC-Date
    error: missing required header WARC-Record-ID
    error: responses for http/https should have Content-Type of application/http; msgtype=response or application/http, saw text/plain
    error: WARC-IP-Address should be used for http and https responses
  WARC-Record-ID None
    WARC-Type resource
    digest not present
    error: missing required header WARC-Date
    error: missing required header WARC-Record-ID
    error: recource records for dns: shall have Content-Type of text/dns, saw text/plain
  WARC-Record-ID None
    WARC-Type resource
    digest not present
    error: missing required header WARC-Date
    error: missing required header WARC-Record-ID
  WARC-Record-ID None
    WARC-Type request
    digest not present
    error: missing required header WARC-Date
    error: missing required header WARC-Record-ID
    error: requests for http/https should have Content-Type of application/http; msgtype=request or application/http, saw text/plain
    error: WARC-IP-Address should be used for http and https requests
  WARC-Record-ID None
    WARC-Type metadata
    digest not present
    error: missing required header WARC-Date
    error: missing required header WARC-Record-ID
    comment: warc-fields body present but empty
  WARC-Record-ID None
    WARC-Type revisit
    digest not present
    error: missing required header Content-Type
    error: missing required header WARC-Date
    error: missing required header WARC-Record-ID
    error: missing required header WARC-Target-URI
    comment: extension seen warc-profile none
    comment: no revisit details validation done due to unknown profile
  WARC-Record-ID None
    WARC-Type revisit
    digest not present
    error: missing required header Content-Type
    error: missing required header WARC-Date
    error: missing required header WARC-Record-ID
    error: missing required header WARC-Target-URI
    error: missing required header WARC-Payload-Digest
    recommendation: missing recommended header WARC-Refers-To
    recommendation: missing recommended header WARC-Refers-To-Date
    recommendation: missing recommended header WARC-Refers-To-Target-URI
  WARC-Record-ID None
    WARC-Type revisit
    digest not present
    error: missing required header Content-Type
    error: missing required header WARC-Date
    error: missing required header WARC-Record-ID
    error: missing required header WARC-Target-URI
    recommendation: missing recommended header WARC-Refers-To
    recommendation: missing recommended header WARC-Refers-To-Date
    comment: extension seen warc-profile http://netpreserve.org/warc/1.0/revisit/server-not-modified
  WARC-Record-ID None
    WARC-Type conversion
    digest not present
    error: missing required header WARC-Date
    error: missing required header WARC-Record-ID
    error: missing required header WARC-Target-URI
  WARC-Record-ID None
    WARC-Type continuation
    digest not present
    error: missing required header WARC-Date
    error: missing required header WARC-Record-ID
    error: missing required header WARC-Segment-Origin-ID
    error: missing required header WARC-Target-URI
    error: continuation record must have WARC-Segment-Number > 1, saw 1
    comment: warcio test continuation code has not been tested, expect bugs
"""

    value = helper(args, 0)
    print(remove_before_test_data(value))
    assert remove_before_test_data(value) == expected


def test_torture_validate_field():
    files = ['standard-torture-validate-field.warc']
    files = [get_test_file(filename) for filename in files]

    args = ['test']
    args.extend(files)

    expected = """\
test/data/standard-torture-validate-field.warc
  WARC-Record-ID <foo:bar>
    WARC-Type does-not-exist
    unknown hash algorithm name in block digest
    error: uri must not be within <> warc-target-uri <http://example.com/>
    error: invalid uri scheme, bad character warc-target-uri <http://example.com/>
    error: duplicate field seen warc-target-uri example.com
    error: invalid uri, no scheme warc-target-uri example.com
    error: duplicate field seen warc-target-uri ex ample.com
    error: invalid uri, no scheme warc-target-uri ex ample.com
    error: invalid uri, contains whitespace warc-target-uri ex ample.com
    error: invalid uri scheme, bad character warc-target-uri ex ample.com
    error: duplicate field seen warc-target-uri h<>ttp://example.com/
    error: invalid uri scheme, bad character warc-target-uri h<>ttp://example.com/
    error: duplicate field seen warc-type CAPITALIZED
    error: uri must be within <> warc-concurrent-to http://example.com/
    error: duplicate field seen warc-date 2017-03-06T04:03:53.Z
    error: WARC 1.0 may not have fractional seconds warc-date 2017-03-06T04:03:53.Z
    error: must contain a / content-type asdf
    error: invalid subtype content-type asdf
    error: duplicate field seen content-type has space/asdf
    error: invalid type content-type has space/asdf
    error: duplicate field seen content-type asdf/has space
    error: invalid subtype content-type asdf/has space
    error: duplicate field seen content-type asdf/has space;asdf
    error: invalid subtype content-type asdf/has space;asdf
    error: missing algorithm warc-block-digest asdf
    error: duplicate field seen warc-block-digest has space:asdf
    error: invalid algorithm warc-block-digest has space:asdf
    error: duplicate field seen warc-block-digest sha1:&$*^&*^#*&^
    error: uri must be within <> warc-warcinfo-id asdf:asdf
    error: duplicate field seen warc-profile http://netpreserve.org/warc/1.0/revisit/identical-payload-digest
    error: must contain a / warc-identified-payload-type asdf
    error: invalid subtype warc-identified-payload-type asdf
    error: uri must be within <> warc-segment-origin-id http://example.com
    error: must be an integer warc-segment-number not-an-integer
    error: duplicate field seen warc-segment-number 0
    error: must be 1 or greater warc-segment-number 0
    error: non-continuation records must always have WARC-Segment-Number = 1 warc-segment-number 0
    error: duplicate field seen warc-segment-number 1
    error: duplicate field seen warc-segment-number 2
    error: non-continuation records must always have WARC-Segment-Number = 1 warc-segment-number 2
    error: duplicate field seen warc-segment-total-length not-an-integer
    error: must be an integer warc-segment-total-length not-an-integer
    comment: unknown WARC-Type warc-type does-not-exist
    comment: WARC-Type is not lower-case warc-type CAPITALIZED
    comment: unknown WARC-Type warc-type CAPITALIZED
    comment: unknown digest algorithm warc-block-digest asdf
    comment: Invalid-looking digest value warc-block-digest sha1:&$*^&*^#*&^
    comment: did not check ip address format, install ipaddress module from pypi if you care
    comment: extension seen warc-truncated invalid
    comment: extension seen warc-profile asdf
    comment: extension seen warc-profile http://netpreserve.org/warc/1.0/revisit/identical-payload-digest
    comment: field was introduced after this warc version WARC-Refers-To-Target-URI http://example.com 1.0
    comment: field was introduced after this warc version WARC-Refers-To-Date not-a-date 1.0
    comment: unknown field, no validation performed WARC-Unknown-Field asdf
  WARC-Record-ID None
    WARC-Type invalid
    digest not present
    error: duplicate field seen warc-date 2017-03-06T04:03:53.Z
    error: fractional seconds must have 1-9 digits warc-date 2017-03-06T04:03:53.Z
    comment: unknown WARC-Type warc-type invalid
  WARC-Record-ID None
    WARC-Type request
    digest not present
    error: missing required header Content-Type
    error: missing required header WARC-Date
    error: missing required header WARC-Record-ID
    error: missing required header WARC-Target-URI
    recommendation: do not segment WARC-Type request
    comment: no configuration seen for WARC-Segment-Number request
"""

    value = helper(args, 0)
    print(remove_before_test_data(value))
    assert remove_before_test_data(value) == expected


def test_arc():
    files = ['does-not-exist.arc']
    files = [get_test_file(filename) for filename in files]

    args = ['test']
    args.extend(files)

    expected = """\
test/data/does-not-exist.arc
"""

    value = helper(args, 0)
    assert remove_before_test_data(value) == expected
