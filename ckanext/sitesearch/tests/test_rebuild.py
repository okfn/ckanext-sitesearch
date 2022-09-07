import pytest

from ckan.lib.search import clear_all
from ckan.tests import factories, helpers


@pytest.fixture(scope="class")
def reset():
    yield
    helpers.reset_db()
    clear_all()


@pytest.mark.usefixtures("reset")
class TestOrgMetadataUpdate(object):
    def test_org_package_count_is_updated(self):
        org = factories.Organization()

        result = helpers.call_action("organization_search", {}, q="*:*")
        assert result["count"] == 1
        assert result["results"][0]["package_count"] == 0

        dataset = helpers.call_action(
            "package_create", {}, name="testing-package", owner_org=org["id"]
        )

        result = helpers.call_action("organization_search", {}, q="*:*")
        assert result["count"] == 1
        assert result["results"][0]["package_count"] == 1

        helpers.call_action(
            "package_delete",
            {},
            id=dataset["id"],
        )

        result = helpers.call_action("organization_search", {}, q="*:*")
        assert result["count"] == 1
        assert result["results"][0]["package_count"] == 0
