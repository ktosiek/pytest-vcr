# -*- coding: utf-8 -*-

import pytest


def pytest_addoption(parser):
    group = parser.getgroup('vcr')
    group.addoption(
        '--vcr-record-mode',
        action='store',
        dest='vcr_record_mode',
        default=None,
        choices=['once', 'new_episodes', 'none', 'all'],
        help='Set the recording mode for VCR.py.'
    )


@pytest.fixture
def vcr_cassette_name(request):
    f = request.function
    if hasattr(f, '__self__'):
        return f.__self__.__class__.__name__ + '.' + f.__name__
    return f.__name__
