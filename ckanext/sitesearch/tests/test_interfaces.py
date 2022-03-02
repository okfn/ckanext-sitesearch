import pytest
import ckan.plugins as p

from ckan.tests import helpers

from ckanext.sitesearch.interfaces import ISiteSearch


class FakeSiteSearchPlugin(p.SingletonPlugin):
    p.implements(ISiteSearch)

    before_organization_search_called = False
    after_organization_search_called = False
    before_group_search_called = False
    after_group_search_called = False
    before_user_search_called = False
    after_user_search_called = False
    before_site_search_called = False
    after_site_search_called = False
    before_page_search_called = False
    after_page_search_called = False

    def before_organization_search(self, search_params):
        self.before_organization_search_called = True
        return search_params

    def after_organization_search(self, search_results, search_params):
        self.after_organization_search_called = True
        return search_results

    def before_group_search(self, search_params):
        self.before_group_search_called = True
        return search_params

    def after_group_search(self, search_results, search_params):
        self.after_group_search_called = True
        return search_results

    def before_user_search(self, search_params):
        self.before_user_search_called = True
        return search_params

    def after_user_search(self, search_results, search_params):
        self.after_user_search_called = True
        return search_results

    def before_site_search(self, search_params):
        self.before_site_search_called = True
        return search_params

    def after_site_search(self, search_results, search_params):
        self.after_site_search_called = True
        return search_results

    def before_page_search(self, search_params):
        self.before_page_search_called = True
        return search_params

    def after_page_search(self, search_results, search_params):
        self.after_page_search_called = True
        return search_results


@pytest.fixture
def fake_plugin():
    """Returns a temporary Plugin for testing.

    Since plugins are Singletons, we need to create a temporary child class
    so attributes are not overriden on each test execution.
    """

    class TempSiteSearchClass(FakeSiteSearchPlugin):
        pass

    return TempSiteSearchClass()


def test_interfaces_entities_search(fake_plugin):
    assert not fake_plugin.before_organization_search_called
    assert not fake_plugin.after_organization_search_called
    helpers.call_action("organization_search")
    assert fake_plugin.before_organization_search_called
    assert fake_plugin.after_organization_search_called

    assert not fake_plugin.before_group_search_called
    assert not fake_plugin.after_group_search_called
    helpers.call_action("group_search")
    assert fake_plugin.before_group_search_called
    assert fake_plugin.after_group_search_called

    assert not fake_plugin.before_user_search_called
    assert not fake_plugin.after_user_search_called
    helpers.call_action("user_search")
    assert fake_plugin.before_user_search_called
    assert fake_plugin.after_user_search_called

    assert not fake_plugin.before_page_search_called
    assert not fake_plugin.after_page_search_called
    helpers.call_action("page_search")
    assert fake_plugin.before_page_search_called
    assert fake_plugin.after_page_search_called


def test_site_search_interface(fake_plugin):
    assert not fake_plugin.before_site_search_called
    assert not fake_plugin.after_site_search_called
    helpers.call_action("site_search")
    assert fake_plugin.before_site_search_called
    assert fake_plugin.after_site_search_called


def test_site_search_calls_other_before_after_search(fake_plugin):
    helpers.call_action("site_search")
    assert fake_plugin.before_organization_search_called
    assert fake_plugin.after_organization_search_called
    assert fake_plugin.before_group_search_called
    assert fake_plugin.after_group_search_called
    assert fake_plugin.before_user_search_called
    assert fake_plugin.after_user_search_called
    assert fake_plugin.before_page_search_called
    assert fake_plugin.after_page_search_called
