from __future__ import absolute_import
from __future__ import unicode_literals

from setuptools import setup

with open('README.md') as f:
    readme = f.read()

with open('requirements.txt') as f:
    requirements = f.read().splitlines()

with open('VERSION') as f:
    version = f.read().strip()

setup(
    name='lcd_st7032',
    version=version,
    url='https://github.com/zakkie/py_lcd_st7032',
    author_email='zakkie@live.jp',
    description='Python module for ST7032 LCD controller with I2C interface.',
    long_description=readme,
    packages=[
        'lcd_st7032',
    ],
    install_requires=requirements,
    keywords='I2C lcd',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'License :: OSI Approved :: MIT License',
    ],
    license='MIT',
)