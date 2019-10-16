from setuptools import setup


setup(
    name="pymbtiles",
    version="0.4.0",
    packages=["pymbtiles"],
    url="https://github.com/consbio/pymbtiles",
    license="ISC",
    author="Brendan C. Ward",
    author_email="bcward@astutespruce.com",
    description="MapBox Mbtiles Utilities",
    long_description_content_type="text/markdown",
    long_description=open("README.md").read(),
    install_requires=[],
    extras_require={
        'test': ['pytest', 'pytest-cov'],
    },
    include_package_data=True,
)
