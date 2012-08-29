#!/usr/bin/env python
# -*- coding: utf-8 -*-
try:
    from setuptools import setup
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup

setup(
    name='django-biscuit',
    version='0.9.12-alpha',
    description='A flexible & capable API layer for Django.',
    author='Daniel Lindsley',
    author_email='daniel@toastdriven.com',
    url='http://github.com/toastdriven/django-biscuit/',
    long_description=open('README.rst', 'r').read(),
    packages=[
        'biscuit',
        'biscuit.utils',
        'biscuit.management',
        'biscuit.management.commands',
        'biscuit.migrations',
        'biscuit.contrib',
        'biscuit.contrib.gis',
    ],
    package_data={
        'biscuit': ['templates/biscuit/*'],
    },
    zip_safe=False,
    requires=[
        'mimeparse',
        'dateutil(>=1.5, !=2.0)',
    ],
    install_requires=[
        'mimeparse',
        'python_dateutil >= 1.5, != 2.0',
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Utilities'
    ],
)
