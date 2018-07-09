#!/usr/bin/env python
import ast
import os
import sys
import codecs
import re

from setuptools import setup, find_packages

ROOT = os.path.realpath(os.path.dirname(__file__))
init = os.path.join(ROOT, 'src', 'dynamic_serializer', '__init__.py')
_version_re = re.compile(r'__version__\s+=\s+(.*)')
_name_re = re.compile(r'NAME\s+=\s+(.*)')

sys.path.insert(0, os.path.join(ROOT, 'src'))

with open(init, 'rb') as f:
    content = f.read().decode('utf-8')
    VERSION = str(ast.literal_eval(_version_re.search(content).group(1)))
    NAME = str(ast.literal_eval(_name_re.search(content).group(1)))


def read(*files):
    content = []
    for f in files:
        content.extend(codecs.open(os.path.join(ROOT, 'src', 'requirements', f), 'r').readlines())
    return "\n".join(filter(lambda l: not l.startswith('-'), content))


install_requires = read('install.pip')
tests_requires = read('testing.pip')

setup(
    name=NAME,
    version=VERSION,
    url='https://github.com/saxix/drf-dynamic-serializer',
    author='Stefano Apostolico',
    author_email='s.apostolico@gmail.com',
    license="MIT",
    description='DjangoRestFramework Dynamic Serializer',
    package_dir={'': 'src'},
    packages=find_packages('src'),
    include_package_data=True,
    install_requires=install_requires,
    tests_require=tests_requires,
    extras_require={
        'tests': tests_requires,
    },
    platforms=['linux'],
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Framework :: Django :: 1.9',
        'Framework :: Django :: 1.10',
        'Framework :: Django :: 1.11',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Intended Audience :: Developers'
    ]
)
