import pytest

from ckan.lib.search.common import make_connection

from ckanext.sitesearch.lib.index import clear_all


@pytest.fixture
def solr():

    return make_connection()


@pytest.fixture
def clean_index():
    clear_all()
