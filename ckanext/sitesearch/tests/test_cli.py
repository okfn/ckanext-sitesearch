import pytest

from ckan import model
from ckan.plugins import toolkit
import ckan.tests.factories as factories
import ckan.tests.helpers as helpers
from ckan.cli.cli import ckan


@pytest.mark.usefixtures("clean_db", "clean_index")
class TestSiteSearchCLI:
    def test_rebuild_orgs(self, cli):

        org = factories.Organization()

        # Update the db directly
        db_obj = model.Group.get(org["id"])
        db_obj.title = "Updated title"
        db_obj.save()

        assert (
            helpers.call_action("organization_search", q='title:"Updated title"')[
                "count"
            ]
            == 0
        )
        result = cli.invoke(ckan, ["sitesearch", "rebuild", "organizations"])
        assert not result.exit_code

        assert (
            helpers.call_action("organization_search", q='title:"Updated title"')[
                "count"
            ]
            == 1
        )

    def test_rebuild_groups(self, cli):

        group = factories.Group()

        # Update the db directly
        db_obj = model.Group.get(group["id"])
        db_obj.title = "Updated title"
        db_obj.save()

        assert (
            helpers.call_action("group_search", q='title:"Updated title"')["count"] == 0
        )
        result = cli.invoke(ckan, ["sitesearch", "rebuild", "groups"])
        assert not result.exit_code

        assert (
            helpers.call_action("group_search", q='title:"Updated title"')["count"] == 1
        )

    def test_rebuild_users(self, cli):

        user = factories.User()

        # Update the db directly
        db_obj = model.User.get(user["id"])
        db_obj.fullname = "Updated fullname"
        db_obj.save()

        assert (
            helpers.call_action("user_search", q='fullname:"Updated fullname"')["count"]
            == 0
        )
        result = cli.invoke(ckan, ["sitesearch", "rebuild", "users"])
        assert not result.exit_code

        assert (
            helpers.call_action("user_search", q='fullname:"Updated fullname"')["count"]
            == 1
        )

    def test_core_search_index_rebuild_does_not_clear_the_rest(self, cli):

        org = factories.Organization()
        factories.Dataset(owner_org=org["id"])

        if toolkit.check_ckan_version(min_version="2.10"):
            result = cli.invoke(ckan, ["search-index", "rebuild"])
        else:
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

    def test_rebuild_pages_invoked_correctly(self, cli):
        result = cli.invoke(ckan, ["sitesearch", "rebuild", "pages"])
        assert not result.exit_code
