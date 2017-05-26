#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import codecs
from setuptools import setup


def read(fname):
    file_path = os.path.join(os.path.dirname(__file__), fname)
    return codecs.open(file_path, encoding='utf-8').read()


setup(
    name='pytest-vcr',
    version='0.3.0',
    author='Tomasz Kontusz',
    author_email='tomasz.kontusz@gmail.com',
    maintainer='Tomasz Kontusz',
    maintainer_email='tomasz.kontusz@gmail.com',
    license='MIT',
    url='https://github.com/ktosiek/pytest-vcr',
    description='Plugin for managing VCR.py cassettes',
    long_description=read('README.rst'),
    py_modules=['pytest_vcr'],
    install_requires=['pytest>=3.0.0', 'vcrpy'],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Framework :: Pytest',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Testing',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
        'Operating System :: OS Independent',
        'License :: OSI Approved :: MIT License',
    ],
    entry_points={
        'pytest11': [
            'vcr = pytest_vcr',
        ],
    },
)
