import pytest

from ckan.plugins import toolkit
from ckan.tests import factories


def test_auth_organization_search():
    """All users can search organizations"""
    context = {"user": ""}
    assert toolkit.check_access("organization_search", context)


def test_auth_group_search():
    """All users can search groups"""
    context = {"user": ""}
    assert toolkit.check_access("group_search", context)


@pytest.mark.usefixtures("clean_db")
def test_auth_user_search():
    """Only sysadmins can search users"""
    context = {"user": ""}
    with pytest.raises(toolkit.NotAuthorized):
        toolkit.check_access("user_search", context)

    sysadmin = factories.Sysadmin()
    context = {"user": sysadmin["name"]}
    assert toolkit.check_access("user_search", context)


def test_auth_site_search():
    """All users can search the whole site

    (but only get results they are authorized to get)"""
    context = {"user": ""}
    assert toolkit.check_access("site_search", context)


def test_auth_page_search():
    """All users can search pages (permission labels apply on private pages)"""
    context = {"user": ""}
    assert toolkit.check_access("page_search", context)
