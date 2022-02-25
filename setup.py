# -*- coding: utf-8 -*-
import os
from setuptools import (
    find_packages,
    setup,
)


with open(os.path.join(os.path.dirname(__file__), 'README.md')) as readme:
    README = readme.read()

with open('requirements.txt') as requirements:
    required = requirements.read().splitlines()


def get_packages(package):
    """
    Return root package and all sub-packages.
    """
    return [
        dirpath for dirpath, dirnames, filenames in os.walk(package)
        if os.path.exists(os.path.join(dirpath, '__init__.py'))]


# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='drf-fancy-permissions',
    version='1.0.0',
    include_package_data=True,
    description='Utilities for defining fine-grained permissions in the Django Rest Framework based API views',
    long_description=README,
    long_description_content_type='text/markdown',
    author='IIIT',
    author_email='github@iiit.pl',
    packages=find_packages(exclude=[
        'testproject',
        'testproject.*',
    ]),
    install_requires=required,
    test_suite='testproject.runtests.run_tests',
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
    ],
)
