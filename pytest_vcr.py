# -*- coding: utf-8 -*-
import os

import pytest
from vcr import VCR


def pytest_addoption(parser):
    group = parser.getgroup('vcr')
    group.addoption(
        '--vcr-record',
        action='store',
        dest='vcr_record',
        default=None,
        choices=['once', 'new_episodes', 'none', 'all'],
        help='Set the recording mode for VCR.py.'
    )
    # TODO: deprecated, remove in a future release
    group.addoption(
        '--vcr-record-mode',
        action='store',
        dest='vcr_record',
        default=None,
        choices=['once', 'new_episodes', 'none', 'all'],
        help='DEPRECATED: use --vcr-record'
    )
    group.addoption(
        '--disable-vcr',
        action='store_true',
        dest='disable_vcr',
        help='Run tests without playing back from VCR.py cassettes'
    )


def pytest_load_initial_conftests(early_config, parser, args):
    early_config.addinivalue_line(
        'markers',
        'vcr: Mark the test as using VCR.py.')


@pytest.fixture(autouse=True)
def _vcr_marker(request):
    marker = request.node.get_marker('vcr')
    if marker:
        request.getfixturevalue('vcr_cassette')


@pytest.fixture(scope='module')
def vcr(request, pytestconfig, vcr_config, vcr_cassette_dir, ):
    """The VCR instance"""
    kwargs = dict(
        cassette_library_dir=vcr_cassette_dir,
        path_transformer=VCR.ensure_suffix(".yaml"),
    )
    kwargs.update(vcr_config)
    record_mode = request.config.getoption('--vcr-record-mode')
    if record_mode:
        pytestconfig.warn("C1",
                          "--vcr-record-mode has been deprecated and will be removed in a future "
                          "release. Use --vcr-record instead.")
    record_mode = request.config.getoption('--vcr-record') or record_mode
    if record_mode:
        kwargs['record_mode'] = record_mode

    disable_vcr = request.config.getoption('--disable-vcr')
    if disable_vcr:
        # Set mode to record but discard all responses to disable both recording and playback
        kwargs['record_mode'] = 'new_episodes'
        kwargs['before_record_response'] = lambda *args, **kwargs: None

    vcr = VCR(**kwargs)
    return vcr


@pytest.fixture
def vcr_cassette(request, vcr, vcr_cassette_name):
    """Wrap a test in a VCR.py cassette"""
    marker = request.node.get_marker('vcr')
    record_mode = request.config.getoption('--vcr-record-mode')
    record_mode = request.config.getoption('--vcr-record') or record_mode

    kwargs = {}
    if marker:
        kwargs.update(marker.kwargs)
    if record_mode:
        kwargs['record_mode'] = record_mode

    disable_vcr = request.config.getoption('--disable-vcr')
    if disable_vcr:
        # Set mode to record but discard all responses to disable both recording and playback
        kwargs['record_mode'] = 'new_episodes'
        kwargs['before_record_response'] = lambda *args, **kwargs: None

    with vcr.use_cassette(vcr_cassette_name, **kwargs) as cassette:
        yield cassette


@pytest.fixture(scope='module')
def vcr_cassette_dir(request):
    test_dir = request.node.fspath.dirname
    return os.path.join(test_dir, 'cassettes')


@pytest.fixture
def vcr_cassette_name(request):
    """Name of the VCR cassette"""
    f = request.function
    if hasattr(f, '__self__'):
        return f.__self__.__class__.__name__ + '.' + request.node.name
    return request.node.name


@pytest.fixture(scope='module')
def vcr_config():
    """Custom configuration for VCR.py"""
    return {}
