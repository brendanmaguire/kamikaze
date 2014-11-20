#!/usr/bin/env python
# -*- coding: utf-8 -*-


try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

__version__ = None
exec(open('kamikaze/_version.py').read())
readme = open('README.rst').read()

requirements = [
    'argh==0.26.1',
    'asyncio-redis==0.13.4',
    'redis==2.10.3',
    'tabulate==0.7.3',
    'wheel==0.24.0',
]

setup(
    name='kamikaze',
    version=__version__,
    description=(
        'A service for placing prioritised packages with expiry times on a '
        'queue and having a consumer notified of the packages'),
    long_description=readme,
    author='Brendan Maguire',
    author_email='maguire.brendan@gmail.com',
    url='https://github.com/brendanmaguire/kamikaze',
    packages=['kamikaze'],
    package_dir={'kamikaze': 'kamikaze'},
    include_package_data=True,
    install_requires=requirements,
    license="BSD",
    keywords='kamikaze',
    classifiers=[
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
    ],
    scripts=['bin/kamikaze'],
    test_suite='tests',
)
