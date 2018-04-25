import os
from setuptools import setup


long_description = 'Utility to read and write Mapbox mbtiles'


if os.path.exists('README.md'):
    try:
        # Use pypandoc to convert markdown readme to reStructuredText as required by pypi
        # Requires pandoc to be installed.  See: http://johnmacfarlane.net/pandoc/installing.html
        from pypandoc import convert
        read_md = lambda f: convert(f, 'rst', format='md')
        long_description = read_md('README.md')
    except:
        pass


setup(
    name='pymbtiles',
    version='0.2.0',
    packages=['pymbtiles'],
    url='https://github.com/consbio/pymbtiles',
    license='ISC',
    author='Brendan Ward',
    author_email='bcward@consbio.org',
    description='MapBox Mbtiles Utilities',
    long_description=long_description,
    install_requires=[],
    include_package_data=True,
    extras_require={
        'test': ['pytest', 'pytest-cov'],
    }
)
