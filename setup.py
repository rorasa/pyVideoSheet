#!/usr/bin/env python

from setuptools import setup, find_packages

setup(
    name='pyVideoSheet',
    version='1.0',
    packages = find_packages(),

    package_data = {'':['*.ttf']},

    description='Python video contact sheet generator',
    author='Wattanit Hotrakool',
    author_email='wattanit.h@gmail.com',
    url='https://github.com/rorasa/pyVideoSheet',
    license='MPL 2.0',
)
