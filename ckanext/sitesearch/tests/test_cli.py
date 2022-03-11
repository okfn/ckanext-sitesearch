import pytest

from ckan import model
import ckan.tests.factories as factories
import ckan.tests.helpers as helpers
from ckan.cli.cli import ckan


@pytest.mark.usefixtures("clean_db", "clean_index")
class TestSiteSearchCLI:

    def test_core_search_index_rebuild_with_r_does_not_clear_the_rest(self, cli):

        org = factories.Organization()
        factories.Dataset(owner_org=org["id"])

        result = cli.invoke(ckan, ["search-index", "rebuild", "-r"])
        assert not result.exit_code
        search_result = helpers.call_action("organization_search")
        assert search_result["count"] == 1
        assert search_result["results"][0]["id"] == org["id"]

    def test_rebuild_datasets_does_not_clear_the_rest(self, cli):

        org = factories.Organization()
        factories.Dataset(owner_org=org["id"])

        result = cli.invoke(ckan, ["sitesearch", "rebuild", "datasets"])
        assert not result.exit_code
        search_result = helpers.call_action("organization_search")
        assert search_result["count"] == 1
        assert search_result["results"][0]["id"] == org["id"]
