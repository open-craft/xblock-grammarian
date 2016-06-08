# -*- coding: utf-8 -*-

# Imports ###########################################################

import os
from setuptools import setup


# Functions #########################################################

def package_data(pkg, root_list):
    """Generic function to find package_data for `pkg` under `root`."""
    data = []
    for root in root_list:
        for dirname, _, files in os.walk(os.path.join(pkg, root)):
            for fname in files:
                data.append(os.path.relpath(os.path.join(dirname, fname), pkg))

    return {pkg: data}


# Main ##############################################################

setup(
    name='xblock-grammarian',
    version='0.1',
    description='Grammarian XBlock',
    packages=['grammarian'],
    install_requires=[
        'Jinja2',
        'XBlock',
        'xblock-utils',
    ],
    entry_points={
        'xblock.v1': 'grammarian = grammarian:GrammarianXBlock',
    },
    package_data=package_data("grammarian", ["templates", "public"]),
)
