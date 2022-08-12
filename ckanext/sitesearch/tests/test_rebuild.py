import pytest

from ckan.tests import factories, helpers


@pytest.mark.usefixtures("clean_db", "clean_index")
class TestOrgMetadataUpdate(object):

    def test_org_package_count_is_updated(self):
        org = factories.Organization()

        result = helpers.call_action("organization_search", {}, q="*:*")
        assert result["count"] == 1
        assert result["results"][0]["package_count"] == 0

        helpers.call_action(
            "package_create",
            {},
            name="testing-package",
            owner_org=org["id"]
        )

        result = helpers.call_action("organization_search", {}, q="*:*")
        assert result["count"] == 1
        assert result["results"][0]["package_count"] == 1
