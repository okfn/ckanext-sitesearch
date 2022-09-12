import pytest

from ckan.lib.search import clear_all as reset_index
from ckan.tests import factories, helpers


@pytest.mark.usefixtures("clean_db", "clean_index")
class TestRebuild:
    @classmethod
    def teardown_class(cls):
        helpers.reset_db()
        reset_index()

    def test_organization_package_count_is_updated(self):
        org = factories.Organization()

        result = helpers.call_action("organization_search", {}, q="*:*")
        assert result["count"] == 1
        assert result["results"][0]["package_count"] == 0

        dataset = helpers.call_action(
            "package_create", {}, name="testing-package", owner_org=org["id"]
        )
        helpers.call_action(
            "package_create", {}, name="testing-package-2", owner_org=org["id"]
        )

        result = helpers.call_action("organization_search", {}, q="*:*")
        assert result["count"] == 1
        assert result["results"][0]["package_count"] == 2

        helpers.call_action(
            "package_delete",
            {},
            id=dataset["id"],
        )

        result = helpers.call_action("organization_search", {}, q="*:*")
        assert result["count"] == 1
        assert result["results"][0]["package_count"] == 1

    def test_group_package_count_is_updated(self):
        group = factories.Group()
        org = factories.Organization()

        result = helpers.call_action("group_search", {}, q="*:*")
        assert result["count"] == 1
        assert result["results"][0]["package_count"] == 0

        dataset = factories.Dataset(owner_org=org["id"])
        dataset2 = factories.Dataset(owner_org=org["id"])

        helpers.call_action(
            "member_create",
            object=dataset["id"],
            id=group["id"],
            object_type="package",
            capacity="member",
        )
        helpers.call_action(
            "member_create",
            object=dataset2["id"],
            id=group["id"],
            object_type="package",
            capacity="member",
        )

        result = helpers.call_action("group_search", {}, q="*:*")
        assert result["count"] == 1
        assert result["results"][0]["package_count"] == 2

        helpers.call_action(
            "package_delete",
            {},
            id=dataset["id"],
        )

        result = helpers.call_action("group_search", {}, q="*:*")
        assert result["count"] == 1
        assert result["results"][0]["package_count"] == 1

    def test_orgs_are_rebuild_when_updating_package_owner_org(self):
        org = factories.Organization()
        dataset = factories.Dataset(owner_org=org["id"])

        result = helpers.call_action("organization_search", {}, q="*:*")
        assert result["count"] == 1
        assert result["results"][0]["package_count"] == 1

        new_org = factories.Organization()

        helpers.call_action(
            "package_update", {}, id=dataset["id"], owner_org=new_org["id"]
        )

        result = helpers.call_action("organization_search", {}, q=f'name:{org["name"]}')
        assert result["count"] == 1
        assert result["results"][0]["package_count"] == 0

        result = helpers.call_action(
            "organization_search", {}, q=f'name:{new_org["name"]}'
        )
        assert result["count"] == 1
        assert result["results"][0]["package_count"] == 1
