# -*- coding: utf-8 -*-

import pytest

# Check that the plugin has been properly installed before proceeding
assert pytest.config.pluginmanager.hasplugin("vcr")


def test_iana_example(testdir):
    testdir.makepyfile(**{'subdir/test_iana_example': """
        import pytest
        try:
            from urllib.request import urlopen
        except ImportError:
            from urllib2 import urlopen

        @pytest.mark.vcr
        def test_iana():
            response = urlopen('http://www.iana.org/domains/reserved').read()
            assert b'Example domains' in response
    """})

    result = testdir.runpytest('-v')
    result.assert_outcomes(1, 0, 0)

    cassette_path = testdir.tmpdir.join(
        'subdir', 'cassettes', 'test_iana.yaml')
    assert cassette_path.size() > 50


def test_disable_vcr(testdir):
    testdir.makepyfile(**{'subdir/test_iana_example': """
        import pytest
        try:
            from urllib.request import urlopen
        except ImportError:
            from urllib2 import urlopen

        @pytest.fixture
        def vcr(vcr):
            # Make sure that modifying the VCR instance does not break anything
            vcr.register_matcher('xx', lambda x: x)
            vcr.record_mode = vcr.record_mode
            return vcr

        @pytest.mark.vcr
        def test_disable_vcr_iana_marking():
            response = urlopen('http://www.iana.org/domains/reserved').read()
            assert b'Example domains' in response

        def test_disable_vcr_iana_fixture(vcr_cassette):
            response = urlopen('http://www.iana.org/domains/reserved').read()
            assert b'Example domains' in response

        def test_disable_vcr_iana_vcr(vcr):
            with vcr.use_cassette('test_disable_vcr_iana_vcr'):
                response = urlopen('http://www.iana.org/domains/reserved').read()
            assert b'Example domains' in response
    """})

    result = testdir.runpytest('--vcr-record=none', '-v')
    result.assert_outcomes(0, 0, 3)

    result = testdir.runpytest('--disable-vcr', '--vcr-record=none', '-v')
    result.assert_outcomes(3, 0, 0)

    cassette_dir_path = testdir.tmpdir.join('subdir', 'cassettes')
    assert not cassette_dir_path.check()


def test_disable_vcr_with_existing_cassette(testdir):
    testdir.makepyfile(**{'subdir/test_iana_example': """
        import pytest
        try:
            from urllib.request import urlopen
        except ImportError:
            from urllib2 import urlopen

        @pytest.fixture(scope='module')
        def vcr(vcr):
            # Make sure that modifying the VCR instance does not break anything
            vcr.register_matcher('xx', lambda x: x)
            vcr.record_mode = vcr.record_mode
            return vcr

        @pytest.mark.vcr
        def test_disable_vcr_iana_marking():
            response = urlopen('http://www.iana.org/domains/reserved').read()
            assert b'Example domains' in response

        def test_disable_vcr_iana_fixture(vcr_cassette):
            response = urlopen('http://www.iana.org/domains/reserved').read()
            assert b'Example domains' in response

        def test_disable_vcr_iana_vcr(vcr_cassette, vcr):
            with vcr.use_cassette('test_disable_vcr_iana_vcr'):
                response = urlopen('http://www.iana.org/domains/reserved').read()
            assert b'Example domains' in response
    """})

    cassette_content = '''
version: 1
interactions:
- request:
    body: null
    headers: {}
    method: GET
    uri: http://httpbin.org/ip
  response:
    body: {string: !!python/unicode "From cassette fixture"}
    headers: {}
    status: {code: 200, message: OK}'''

    cassette_dir_path = testdir.tmpdir.join('subdir', 'cassettes').mkdir()
    cassette_dir_path.join('test_disable_vcr_iana_marking.yaml').write(cassette_content)
    cassette_dir_path.join('test_disable_vcr_iana_fixture.yaml').write(cassette_content)
    cassette_dir_path.join('test_disable_vcr_iana_vcr.yaml').write(cassette_content)

    t0 = cassette_dir_path.join('test_disable_vcr_iana_marking.yaml').mtime()

    result = testdir.runpytest('--vcr-record=none', '-v')
    result.assert_outcomes(0, 0, 3)

    result = testdir.runpytest('--disable-vcr', '--vcr-record=none', '-v')
    result.assert_outcomes(3, 0, 0)

    t1 = cassette_dir_path.join('test_disable_vcr_iana_marking.yaml').mtime()
    # Check that the cassette file is unmodified
    assert t0 == t1


def test_custom_matchers(testdir):
    testdir.makepyfile("""
        import pytest
        try:
            from urllib.request import urlopen
        except ImportError:
            from urllib2 import urlopen

        @pytest.fixture(scope='module')
        def vcr(vcr):
            vcr.register_matcher('my_matcher', lambda a, b: True)
            vcr.match_on = ['my_matcher']
            return vcr

        @pytest.mark.vcr
        def test_custom_matchers_iana():
            response = urlopen('http://www.iana.org/domains/reserved').read()
            assert b'From cassette fixture' in response
    """)

    testdir.tmpdir.mkdir('cassettes').join('test_custom_matchers_iana.yaml') \
        .write('''
version: 1
interactions:
- request:
    body: null
    headers: {}
    method: GET
    uri: http://httpbin.org/ip
  response:
    body: {string: !!python/unicode "From cassette fixture"}
    headers: {}
    status: {code: 200, message: OK}''')

    result = testdir.runpytest('-v', '-s', '--vcr-record=none')
    assert result.ret == 0


def test_overriding_cassette_path(testdir):
    testdir.makepyfile(**{'subdir/test_dir': """
        import pytest, os

        @pytest.fixture(scope='module')
        def vcr_cassette_dir(request):
            # Put all cassettes in vhs/{module}/{test}.yaml
            return os.path.join('vhs', request.module.__name__)

        @pytest.mark.vcr
        def test_show_cassette(vcr_cassette):
            print("Cassette: {}".format(vcr_cassette._path))
    """})

    result = testdir.runpytest('-s')
    result.stdout.fnmatch_lines(['*Cassette: vhs/test_dir/test_show_cassette.yaml'])
    result.assert_outcomes(1, 0, 0)


def test_cassette_name_for_classes(testdir):
    testdir.makepyfile("""
        import pytest

        @pytest.mark.vcr
        class TestClass:
            def test_method(self, vcr_cassette_name):
                print("Cassette: {}".format(vcr_cassette_name))
    """)

    result = testdir.runpytest('-s')
    result.stdout.fnmatch_lines(['*Cassette: TestClass.test_method'])


def test_vcr_config(testdir):
    testdir.makepyfile("""
        import pytest

        @pytest.fixture(scope='module')
        def vcr_config():
            return {'record_mode': 'none'}

        @pytest.mark.vcr
        def test_method(vcr_cassette):
            print("Cassette record mode: {}".format(vcr_cassette.record_mode))
    """)

    result = testdir.runpytest('-s')
    result.assert_outcomes(1, 0, 0)
    result.stdout.fnmatch_lines(['*Cassette record mode: none'])


def test_marker_options(testdir):
    testdir.makepyfile("""
        import pytest

        @pytest.fixture(scope='module')
        def vcr_config():
            return {'record_mode': 'all'}

        @pytest.mark.vcr(record_mode='none')
        def test_method(vcr_cassette):
            print("Cassette record mode: {}".format(vcr_cassette.record_mode))
    """)

    result = testdir.runpytest('-s')
    result.assert_outcomes(1, 0, 0)
    result.stdout.fnmatch_lines(['*Cassette record mode: none'])


def test_overriding_record_mode(testdir):
    testdir.makepyfile("""
        import pytest

        @pytest.fixture(scope='module')
        def vcr_config():
            return {'record_mode': 'none'}

        @pytest.mark.vcr(record_mode='once')
        def test_method(vcr_cassette, vcr):
            print("Cassette record mode: {}".format(vcr_cassette.record_mode))
    """)

    result = testdir.runpytest('-s', '--vcr-record', 'all')
    result.assert_outcomes(1, 0, 0)
    result.stdout.fnmatch_lines(['*Cassette record mode: all'])


def test_deprecated_record_mode(testdir):
    testdir.makepyfile("""
        import pytest

        @pytest.fixture(scope='module')
        def vcr_config():
            return {'record_mode': 'none'}

        @pytest.mark.vcr(record_mode='once')
        def test_method(vcr_cassette):
            print("Cassette record mode: {}".format(vcr_cassette.record_mode))
    """)

    result = testdir.runpytest('-s', '--vcr-record-mode', 'all')
    result.assert_outcomes(1, 0, 0)
    result.stdout.fnmatch_lines(['*Cassette record mode: all',
                                 '*--vcr-record-mode has been deprecated*'])


def test_marking_whole_class(testdir):
    testdir.makepyfile("""
        import pytest

        has_cassette = False

        @pytest.yield_fixture
        def vcr_cassette(vcr_cassette):
            global has_cassette
            has_cassette = True
            yield vcr_cassette
            has_cassette = False

        @pytest.mark.vcr
        class TestClass(object):
            def test_method(self):
                assert has_cassette
    """)

    result = testdir.runpytest('-s')
    assert result.ret == 0


def test_separate_cassettes_for_parametrized_tests(testdir):
    testdir.makepyfile("""
        import pytest

        @pytest.mark.vcr
        @pytest.mark.parametrize('arg', ['a', 'b'])
        def test_parameters(arg, vcr_cassette_name):
            assert vcr_cassette_name == 'test_parameters[{}]'.format(arg)
    """)

    result = testdir.runpytest('-s')
    assert result.ret == 0


def test_use_in_function_scope_fixture(testdir):
    """Test that the VCR instance can be used from fixtures and that the cassettes
    land in the correct location."""
    testdir.makepyfile(**{'subdir/test_iana_example': """
        import pytest
        try:
            from urllib.request import urlopen
        except ImportError:
            from urllib2 import urlopen

        @pytest.fixture
        def iana_response(vcr):
            with vcr.use_cassette('iana_response_fixture'):
                response = urlopen('http://www.iana.org/domains/reserved').read()
            return response

        def test_with_fixture(iana_response):
            assert b'Example domains' in iana_response
    """})

    result = testdir.runpytest('-v')
    result.assert_outcomes(1, 0, 0)

    cassette_path = testdir.tmpdir.join(
        'subdir', 'cassettes', 'iana_response_fixture.yaml')
    assert cassette_path.size() > 50


def test_use_in_module_scope_fixture(testdir):
    testdir.makepyfile(**{'subdir/test_iana_example': """
        import pytest
        try:
            from urllib.request import urlopen
        except ImportError:
            from urllib2 import urlopen

        @pytest.fixture(scope='module')
        def iana_response(vcr):
            with vcr.use_cassette('iana_response_fixture'):
                response = urlopen('http://www.iana.org/domains/reserved').read()
            return response

        def test_with_fixture(iana_response):
            assert b'Example domains' in iana_response
    """})

    result = testdir.runpytest('-v')
    result.assert_outcomes(1, 0, 0)

    cassette_path = testdir.tmpdir.join(
        'subdir', 'cassettes', 'iana_response_fixture.yaml')
    assert cassette_path.size() > 50


@pytest.mark.xfail(reason="session-scoped fixtures are not supported")
def test_use_in_session_scope_fixture(testdir):
    testdir.makepyfile(**{'subdir/test_iana_example': """
        import pytest
        try:
            from urllib.request import urlopen
        except ImportError:
            from urllib2 import urlopen

        @pytest.fixture(scope='session')
        def vcr_cassette_dir():
            test_dir = dirname(abspath(__file__))
            return os.path.join(test_dir, 'cassettes')

        @pytest.fixture(scope='session')
        def iana_response(vcr):
            with vcr.use_cassette('iana_response_fixture'):
                response = urlopen('http://www.iana.org/domains/reserved').read()
            return response

        def test_with_fixture(iana_response):
            assert b'Example domains' in iana_response
    """})

    result = testdir.runpytest('-v')
    result.assert_outcomes(1, 0, 0)

    cassette_path = testdir.tmpdir.join(
        'subdir', 'cassettes', 'iana_response_fixture.yaml')
    assert cassette_path.size() > 50


def test_help_message(testdir):
    result = testdir.runpytest(
        '--help',
    )
    # fnmatch_lines does an assertion internally
    result.stdout.fnmatch_lines([
        'vcr:',
        '*--vcr-record={*}',
    ])


def test_marker_message(testdir):
    result = testdir.runpytest('--markers')
    result.stdout.fnmatch_lines([
        '@pytest.mark.vcr: Mark the test as using VCR.py.',
    ])
