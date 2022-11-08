import pytest

import ckan.plugins as plugins
import ckan.plugins.toolkit as tk

from ckan.tests import factories, helpers


def _get_extra_environ(user):
    """ Returns an extra_environ dictionary

    CKAN 2.10 deprecates REMOTE_USER as a valid
    environ variable in favor of an
    Authorization header. This can be removed when
    dropping support for CKAN 2.9.
    """
    extra_environ = {}
    try:
        extra_environ["Authorization"] = user["token"]
    except KeyError:
        extra_environ["REMOTE_USER"] = user["name"]
    return extra_environ


def _get_sysadmin():
    """ Returns a sysadmin user

    CKAN 2.10 requires an Authorization token to
    call app.post() method and exempt CSRF protection.
    This can be removed when dropping support for 2.9
    """
    try:
        return factories.SysadminWithToken()
    except AttributeError:
        return factories.Sysadmin()


class CustomDatasetType(plugins.SingletonPlugin, tk.DefaultDatasetForm):

    plugins.implements(plugins.IDatasetForm, inherit=True)

    def package_types(self):

        return ["custom_dataset"]


@pytest.mark.usefixtures("clean_db", "clean_index")
class TestBlueprint:
    @pytest.mark.ckan_config("ckan.auth.create_unowned_dataset", True)
    def test_search_datasets_returns_only_datasts(self, app):

        sysadmin = _get_sysadmin()

        factories.User()
        factories.Group()
        factories.Dataset()
        factories.Dataset()
        factories.Dataset(type="custom_dataset")

        response = app.get("/dataset?q=*:*")

        assert "3 datasets found" in response.body

        extra_environ = _get_extra_environ(sysadmin)

        response = app.get("/dataset?q=*:*", extra_environ=extra_environ)

        assert "3 datasets found" in response.body


@pytest.mark.usefixtures("clean_db", "clean_index")
class TestDatasetCreationWorkflow:
    @pytest.mark.ckan_config("ckan.auth.create_unowned_dataset", True)
    def test_dataset_creation_workflow_index_properly(self, app):

        sysadmin = _get_sysadmin()
        organization = factories.Organization()

        url = tk.url_for("dataset.new")
        extra_environ = _get_extra_environ(sysadmin)
        app.post(
            url,
            extra_environ=extra_environ,
            data={
                "name": "testing-dataset-flow",
                "owner_org": organization["id"],
                "save": "",
                "_ckan_phase": 1,
            },
            follow_redirects=False,
        )

        # Test we do not index draft package
        assert helpers.call_action("package_search", q="*:*")["count"] == 0
        # Test organization did not index package
        result = helpers.call_action("organization_search", q="*:*")["results"][0]
        assert result["package_count"] == 0

        url = tk.url_for("resource.new", id="testing-dataset-flow")
        app.post(
            url,
            extra_environ=extra_environ,
            data={
                "id": "",
                "url": "http://example.com/resource",
                "save": "go-metadata",
            },
        )

        # Test package is indexed when active
        result = helpers.call_action("package_search", q="*:*")["results"][0]
        assert result["name"] == "testing-dataset-flow"
        assert result["state"] == "active"
        # Test organization indexed the new package
        result = helpers.call_action("organization_search", q="*:*")["results"][0]
        assert result["package_count"] == 1
