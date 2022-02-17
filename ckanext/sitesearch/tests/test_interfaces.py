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


def test_interfaces():
    fake_plugin = FakeSiteSearchPlugin()

    helpers.call_action('organization_search')
    assert fake_plugin.before_organization_search_called
    assert fake_plugin.after_organization_search_called

    helpers.call_action('group_search')
    assert fake_plugin.before_group_search_called
    assert fake_plugin.after_group_search_called

    helpers.call_action('user_search')
    assert fake_plugin.before_user_search_called
    assert fake_plugin.after_user_search_called

    helpers.call_action('site_search')
    assert fake_plugin.before_site_search_called
    assert fake_plugin.after_site_search_called

    helpers.call_action('page_search')
    assert fake_plugin.before_page_search_called
    assert fake_plugin.after_page_search_called
