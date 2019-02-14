from setuptools import setup


setup(
    name="pymbtiles",
    version="0.3.2",
    packages=["pymbtiles"],
    url="https://github.com/consbio/pymbtiles",
    license="ISC",
    author="Brendan Ward",
    author_email="bcward@consbio.org",
    description="MapBox Mbtiles Utilities",
    long_description_content_type="text/markdown",
    long_description=open("README.md").read(),
    install_requires=[],
    include_package_data=True,
)
