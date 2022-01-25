import pytest

import ckan.plugins as plugins
import ckan.plugins.toolkit as tk

from ckan.tests import factories, helpers


class CustomDatasetType(plugins.SingletonPlugin, tk.DefaultDatasetForm):

    plugins.implements(plugins.IDatasetForm, inherit=True)

    def package_types(self):

        return ["custom_dataset"]


@pytest.mark.usefixtures("clean_db", "clean_index")
class TestBlueprint:
    @pytest.mark.ckan_config("ckan.auth.create_unowned_dataset", True)
    def test_search_datasets_returns_only_datasts(self, app):

        sysadmin = factories.Sysadmin()
        factories.User()

        factories.Group()

        factories.Dataset()
        factories.Dataset()
        factories.Dataset(type="custom_dataset")

        response = app.get(u"/dataset?q=*:*")

        assert "3 datasets found" in response.body

        extra_environ = {"REMOTE_USER": sysadmin["name"]}

        response = app.get(u"/dataset?q=*:*", extra_environ=extra_environ)

        assert "3 datasets found" in response.body

