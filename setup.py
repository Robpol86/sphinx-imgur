#!/usr/bin/env python
"""Setup script for the project."""

from __future__ import print_function

from setuptools import Command, setup

IMPORT = 'sphinx_imgur'
INSTALL_REQUIRES = ['sphinx']
LICENSE = 'MIT'
NAME = 'sphinx-imgur'
VERSION = '2.0.1'


class CheckVersion(Command):
    """Make sure version strings and other metadata match here, in module/package, tox, and other places."""

    description = 'verify consistent version/etc strings in project'
    user_options = []

    @classmethod
    def initialize_options(cls):
        """Required by distutils."""

    @classmethod
    def finalize_options(cls):
        """Required by distutils."""

    @classmethod
    def run(cls):
        """Check variables."""
        project = __import__(IMPORT, fromlist=[''])
        for expected, var in [('@Robpol86', '__author__'), (LICENSE, '__license__'), (VERSION, '__version__')]:
            if getattr(project, var) != expected:
                raise SystemExit('Mismatch: {0}'.format(var))


if __name__ == '__main__':
    setup(
        author='@Robpol86',
        author_email='robpol86@gmail.com',
        classifiers=[
            'Development Status :: 5 - Production/Stable',
            'Environment :: MacOS X',
            'Environment :: Plugins',
            'Environment :: Win32 (MS Windows)',
            'Framework :: Sphinx :: Extension',
            'Intended Audience :: Developers',
            'License :: OSI Approved :: MIT License',
            'Operating System :: MacOS :: MacOS X',
            'Operating System :: Microsoft :: Windows',
            'Operating System :: POSIX :: Linux',
            'Operating System :: POSIX',
            'Programming Language :: Python :: 2.7',
            'Programming Language :: Python :: 3.3',
            'Programming Language :: Python :: 3.4',
            'Programming Language :: Python :: Implementation :: PyPy',
            'Topic :: Documentation :: Sphinx',
            'Topic :: Software Development :: Documentation',
        ],
        cmdclass=dict(check_version=CheckVersion),
        description='Sphinx extension that embeds Imgur images, albums, and their metadata in documents.',
        install_requires=INSTALL_REQUIRES,
        keywords='sphinx imgur',
        license=LICENSE,
        long_description='',
        name=NAME,
        packages=['sphinx_imgur'],
        url='https://github.com/Robpol86/' + NAME,
        version=VERSION,
        zip_safe=True,
    )
