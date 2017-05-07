# -*- coding: utf-8 -*-


def test_iana_example(testdir):
    testdir.makepyfile(**{'subdir/test_iana_example': """
        import pytest
        try:
            from urllib.request import urlopen
        except ImportError:
            from urllib2 import urlopen

        @pytest.mark.vcr()
        def test_iana():
            response = urlopen('http://www.iana.org/domains/reserved').read()
            assert b'Example domains' in response
    """})

    result = testdir.runpytest('-v')

    result.stdout.fnmatch_lines(['*::test_iana PASSED'])

    cassette_path = testdir.tmpdir.join(
        'subdir', 'cassettes', 'test_iana.yaml')
    assert cassette_path.size() > 50


def test_overriding_cassette_path(testdir):
    testdir.makepyfile("""
        import pytest, os

        @pytest.fixture
        def vcr_cassette_path(request, vcr_cassette_name):
            # Put all cassettes in vhs/{module}/{test}.yaml
            return os.path.join(
                'vhs', request.module.__name__, vcr_cassette_name)

        @pytest.mark.vcr()
        def test_show_cassette(vcr_cassette):
            print("Cassette: {}".format(vcr_cassette._path))
    """)

    result = testdir.runpytest('-s')
    result.stdout.fnmatch_lines(['*Cassette: vhs/*/test_show_cassette.yaml'])


def test_cassette_name_for_classes(testdir):
    testdir.makepyfile("""
        import pytest

        @pytest.mark.vcr()
        class TestClass:
            def test_method(self, vcr_cassette_name):
                print("Cassette: {}".format(vcr_cassette_name))
    """)

    result = testdir.runpytest('-s')
    result.stdout.fnmatch_lines(['*Cassette: TestClass.test_method'])


def test_vcr_config(testdir):
    testdir.makepyfile("""
        import pytest

        @pytest.fixture
        def vcr_config():
            return {'record_mode': 'none'}

        @pytest.mark.vcr()
        def test_method(vcr_cassette):
            print("Cassette record mode: {}".format(vcr_cassette.record_mode))
    """)

    result = testdir.runpytest('-s')
    result.stdout.fnmatch_lines(['*Cassette record mode: none'])


def test_marker_options(testdir):
    testdir.makepyfile("""
        import pytest

        @pytest.fixture
        def vcr_config():
            return {'record_mode': 'all'}

        @pytest.mark.vcr(record_mode='none')
        def test_method(vcr_cassette):
            print("Cassette record mode: {}".format(vcr_cassette.record_mode))
    """)

    result = testdir.runpytest('-s')
    result.stdout.fnmatch_lines(['*Cassette record mode: none'])


def test_overriding_record_mode(testdir):
    testdir.makepyfile("""
        import pytest

        @pytest.fixture
        def vcr_config():
            return {'record_mode': 'none'}

        @pytest.mark.vcr(record_mode='once')
        def test_method(vcr_cassette):
            print("Cassette record mode: {}".format(vcr_cassette.record_mode))
    """)

    result = testdir.runpytest('-s', '--vcr-record-mode', 'all')
    result.stdout.fnmatch_lines(['*Cassette record mode: all'])


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

        @pytest.mark.vcr()
        class TestClass(object):
            def test_method(self):
                assert has_cassette
    """)

    result = testdir.runpytest('-s')
    assert result.ret == 0


def test_separate_cassettes_for_parametrized_tests(testdir):
    testdir.makepyfile("""
        import pytest

        @pytest.mark.vcr()
        @pytest.mark.parametrize('arg', ['a', 'b'])
        def test_parameters(arg, vcr_cassette_name):
            assert vcr_cassette_name == 'test_parameters[{}]'.format(arg)
    """)

    result = testdir.runpytest('-s')
    assert result.ret == 0


def test_help_message(testdir):
    result = testdir.runpytest(
        '--help',
    )
    # fnmatch_lines does an assertion internally
    result.stdout.fnmatch_lines([
        'vcr:',
        '*--vcr-record-mode={*}',
    ])


def test_marker_message(testdir):
    result = testdir.runpytest('--markers')
    result.stdout.fnmatch_lines([
        '@pytest.mark.vcr: Mark the test as using VCR.py.',
    ])
