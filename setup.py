# -*- coding: utf-8 -*-
# Always prefer setuptools over distutils
from setuptools import setup, find_packages
from codecs import open  # To use a consistent encoding
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the relevant file
with open(path.join(here, "README.md"), encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="""ckanext-sitesearch""",
    version="0.0.6",
    description="""Solr search for other CKAN entities than datasets""",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/okfn/ckanext-sitesearch",
    author="""Adrià Mercader""",
    author_email="""adria.mercader@okfn.org""",
    license="AGPL",
    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        "Development Status :: 4 - Beta",
        "License :: OSI Approved :: GNU Affero General Public License v3 or later (AGPLv3+)",
        "Programming Language :: Python :: 3",
    ],
    # What does your project relate to?
    keywords="""CKAN ckanext search Solr""",
    # You can just specify the packages manually here if your project is
    # simple. Or you can use find_packages().
    packages=find_packages(exclude=["contrib", "docs", "tests*"]),
    namespace_packages=["ckanext"],
    install_requires=[
        # CKAN extensions should not list dependencies here, but in a separate
        # ``requirements.txt`` file.
        #
        # http://docs.ckan.org/en/latest/extensions/best-practices.html
        # add-third-party-libraries-to-requirements-txt
    ],
    include_package_data=True,
    package_data={},
    data_files=[],
    entry_points="""
        [ckan.plugins]
        sitesearch=ckanext.sitesearch.plugin:SitesearchPlugin

        test_dataset_type=ckanext.sitesearch.tests.test_blueprints:CustomDatasetType

        [babel.extractors]
        ckan = ckan.lib.extract:extract_ckan
    """,
    message_extractors={
        "ckanext": [
            ("**.py", "python", None),
            ("**.js", "javascript", None),
            ("**/templates/**.html", "ckan", None),
        ],
    },
)
