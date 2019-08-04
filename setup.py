#!/usr/bin/env python
import os
import re

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


def get_version(package):
    """
    Return package version as listed in `__version__` in `init.py`.
    """
    init_py = open(os.path.join(package, '__init__.py')).read()
    return re.search("__version__ = ['\"]([^'\"]+)['\"]", init_py).group(1)


with open('README.rst') as readme_file:
    readme = readme_file.read()


with open('CHANGELOG.rst') as history_file:
    history = history_file.read()


requirements = [
    'requests>=2.10.0',
]

setup(
    name='appmetrica',
    version=get_version('appmetrica'),
    description='API for integration with Yandex AppMetrica',
    long_description=readme + '\n\n' + history,
    author='MyBook',
    author_email='dev@mybook.ru',
    url='https://github.com/MyBook/appmetrica',
    packages=[
        'appmetrica',
    ],
    package_dir={'appmetrica': 'appmetrica'},
    include_package_data=True,
    install_requires=requirements,
    license='BSD',
    zip_safe=False,
    keywords='appmetrica',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
    test_suite='tests',
)
