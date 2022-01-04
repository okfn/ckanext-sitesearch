import pytest

from ckan.plugins import toolkit
from ckan.tests import factories, helpers

call_action = helpers.call_action


@pytest.mark.usefixtures("clean_db", "clean_index")
def test_org_update():

    sysadmin = factories.Sysadmin()

    org = factories.Organization()

    result = call_action("organization_search", q="snake")

    assert result["count"] == 0

    org["description"] = "Some org about snakes"

    call_action("organization_update", context={"user": sysadmin["name"]}, **org)

    result = call_action("organization_search", q="snake")

    assert result["count"] == 1


@pytest.mark.usefixtures("clean_db", "clean_index")
def test_group_update():

    sysadmin = factories.Sysadmin()

    group = factories.Group()

    result = call_action("group_search", q="snake")

    assert result["count"] == 0

    group["description"] = "Some group about snakes"

    call_action("group_update", context={"user": sysadmin["name"]}, **group)

    result = call_action("group_search", q="snake")

    assert result["count"] == 1


@pytest.mark.usefixtures("clean_db", "clean_index")
def test_user_update():

    sysadmin = factories.Sysadmin()

    user = factories.User()

    result = call_action("user_search", q="snake")

    assert result["count"] == 0

    user["about"] = "The snake user"

    call_action("user_update", context={"user": sysadmin["name"]}, **user)

    result = call_action("user_search", q="snake")

    assert result["count"] == 1


@pytest.mark.usefixtures("clean_db", "clean_index")
def test_org_delete():

    sysadmin = factories.Sysadmin()

    org = factories.Organization(description="Some org about snakes")

    result = call_action("organization_search", q="snake")

    assert result["count"] == 1

    call_action("organization_delete", context={"user": sysadmin["name"]}, id=org["id"])

    result = call_action("organization_search", q="snake")

    assert result["count"] == 0


@pytest.mark.usefixtures("clean_db", "clean_index")
def test_group_delete():

    sysadmin = factories.Sysadmin()

    group = factories.Group(description="Some group about snakes")

    result = call_action("group_search", q="snake")

    assert result["count"] == 1

    call_action("group_delete", context={"user": sysadmin["name"]}, id=group["id"])

    result = call_action("group_search", q="snake")

    assert result["count"] == 0


@pytest.mark.usefixtures("clean_db", "clean_index")
def test_user_delete():

    sysadmin = factories.Sysadmin()

    user = factories.User(about="The snake user")

    result = call_action("user_search", q="snake")

    assert result["count"] == 1

    call_action("user_delete", context={"user": sysadmin["name"]}, id=user["id"])

    result = call_action("user_search", q="snake")

    assert result["count"] == 0
