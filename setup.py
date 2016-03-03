# -*- coding: utf-8 -*-
from setuptools import setup, find_packages
import os

version = '0.0.1'

setup(
    name='property',
    version=version,
    description='Allows Property Management Agencies to manage properties',
    author='Bituls Company Limited',
    author_email='info@bituls.com',
    packages=find_packages(),
    zip_safe=False,
    include_package_data=True,
    install_requires=("frappe",),
)
