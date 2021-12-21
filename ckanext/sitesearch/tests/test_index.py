import pytest

from ckan.plugins import toolkit
from ckan.tests import factories
from ckanext.sitesearch.lib import index


def test_index_no_id():

    with pytest.raises(ValueError):
        index.index_organization({"name": "some_org"})


@pytest.mark.usefixtures("clean_db", "clean_index")
def test_index_org(solr):

    org = factories.Organization()

    index.index_organization(org)

    q = "id:{}".format(org["id"])

    fq = "+site_id:{}".format(toolkit.config.get("ckan.site_id"))

    response = solr.search(q=q, fq=fq)

    assert response.hits == 1
    assert response.docs[0]["id"] == org["id"]

    assert response.docs[0]["entity_type"] == "organization"


@pytest.mark.usefixtures("clean_db", "clean_index")
def test_index_org_default_field(solr):

    org = factories.Organization(
        name="only_in_name",
        title="only_in_title",
        description="only_in_description",
        extras=[{"key": "some_extra", "value": "only_in_extra"}],
    )

    index.index_organization(org)

    fq = "+site_id:{}".format(toolkit.config.get("ckan.site_id"))

    for term in (
        "only_in_name",
        "only_in_title",
        "only_in_description",
        "only_in_extra",
    ):
        response = solr.search(q=term, df="text", fq=fq)

        assert response.hits == 1, term
        assert response.docs[0]["id"] == org["id"]


@pytest.mark.usefixtures("clean_db", "clean_index")
def test_index_group(solr):

    group = factories.Group()

    index.index_group(group)

    q = "id:{}".format(group["id"])

    fq = "+site_id:{}".format(toolkit.config.get("ckan.site_id"))

    response = solr.search(q=q, fq=fq)

    assert response.hits == 1
    assert response.docs[0]["id"] == group["id"]

    assert response.docs[0]["entity_type"] == "group"


@pytest.mark.usefixtures("clean_db", "clean_index")
def test_index_group_default_field(solr):

    group = factories.Group(
        name="only_in_name",
        title="only_in_title",
        description="only_in_description",
        extras=[{"key": "some_extra", "value": "only_in_extra"}],
    )

    index.index_group(group)

    fq = "+site_id:{}".format(toolkit.config.get("ckan.site_id"))

    for term in (
        "only_in_name",
        "only_in_title",
        "only_in_description",
        "only_in_extra",
    ):
        response = solr.search(q=term, df="text", fq=fq)

        assert response.hits == 1, term
        assert response.docs[0]["id"] == group["id"]


@pytest.mark.usefixtures("clean_db", "clean_index")
def test_index_user(solr):

    user = factories.User()

    index.index_user(user)

    q = "id:{}".format(user["id"])

    fq = "+site_id:{}".format(toolkit.config.get("ckan.site_id"))

    response = solr.search(q=q, fq=fq)

    assert response.hits == 1
    assert response.docs[0]["id"] == user["id"]

    assert response.docs[0]["entity_type"] == "user"


@pytest.mark.usefixtures("clean_db", "clean_index")
def test_index_user_default_field(solr):

    user = factories.User(
        name="only_in_name",
        fullname="only_in_fullname",
        about="only_in_about",
        email="only_in_email@example.com",
    )

    index.index_user(user)

    fq = "+site_id:{}".format(toolkit.config.get("ckan.site_id"))

    for term in (
        "only_in_name",
        "only_in_fullname",
        "only_in_about",
        "only_in_email",
    ):
        response = solr.search(q=term, df="text", fq=fq)

        assert response.hits == 1, term
        assert response.docs[0]["id"] == user["id"]


@pytest.mark.usefixtures("clean_db", "clean_index")
def test_delete_org(solr):

    org = factories.Organization()

    index.index_organization(org)

    q = "id:{}".format(org["id"])

    fq = "+site_id:{}".format(toolkit.config.get("ckan.site_id"))

    response = solr.search(q=q, fq=fq)
    assert response.docs[0]["id"] == org["id"]

    index.delete_organization(org["id"])

    response = solr.search(q=q, fq=fq)
    assert response.hits == 0


@pytest.mark.usefixtures("clean_db", "clean_index")
def test_delete_group(solr):

    group = factories.Group()

    index.index_group(group)

    q = "id:{}".format(group["id"])

    fq = "+site_id:{}".format(toolkit.config.get("ckan.site_id"))

    response = solr.search(q=q, fq=fq)
    assert response.docs[0]["id"] == group["id"]

    index.delete_group(group["id"])

    response = solr.search(q=q, fq=fq)
    assert response.hits == 0


@pytest.mark.usefixtures("clean_db", "clean_index")
def test_delete_user(solr):

    user = factories.User()

    index.index_user(user)

    q = "id:{}".format(user["id"])

    fq = "+site_id:{}".format(toolkit.config.get("ckan.site_id"))

    response = solr.search(q=q, fq=fq)
    assert response.docs[0]["id"] == user["id"]

    index.delete_user(user["id"])

    response = solr.search(q=q, fq=fq)
    assert response.hits == 0


@pytest.mark.usefixtures("clean_db", "clean_index")
def test_clear_orgs(solr):

    org1 = factories.Organization()
    org2 = factories.Organization()

    index.index_organization(org1)
    index.index_organization(org2)

    q = "entity_type:organization"

    fq = "+site_id:{}".format(toolkit.config.get("ckan.site_id"))

    response = solr.search(q=q, fq=fq)
    assert response.hits == 2

    index.clear_organizations()

    response = solr.search(q=q, fq=fq)
    assert response.hits == 0


@pytest.mark.usefixtures("clean_db", "clean_index")
def test_clear_groups(solr):

    group1 = factories.Group()
    group2 = factories.Group()

    index.index_group(group1)
    index.index_group(group2)

    q = "entity_type:group"

    fq = "+site_id:{}".format(toolkit.config.get("ckan.site_id"))

    response = solr.search(q=q, fq=fq)
    assert response.hits == 2

    index.clear_groups()

    response = solr.search(q=q, fq=fq)
    assert response.hits == 0


@pytest.mark.usefixtures("clean_db", "clean_index")
def test_clear_users(solr):

    user1 = factories.User()
    user2 = factories.User()

    index.index_user(user1)
    index.index_user(user2)

    q = "entity_type:user"

    fq = "+site_id:{}".format(toolkit.config.get("ckan.site_id"))

    response = solr.search(q=q, fq=fq)
    assert response.hits == 2

    index.clear_users()

    response = solr.search(q=q, fq=fq)
    assert response.hits == 0


@pytest.mark.usefixtures("clean_db", "clean_index")
def test_clear_all(solr):

    org1 = factories.Organization()
    org2 = factories.Organization()

    index.index_organization(org1)
    index.index_organization(org2)

    factories.Dataset(owner_org=org1["id"])
    factories.Dataset(owner_org=org2["id"])

    group1 = factories.Group()
    group2 = factories.Group()

    index.index_group(group1)
    index.index_group(group2)

    user1 = factories.User()
    user2 = factories.User()

    index.index_user(user1)
    index.index_user(user2)

    q = "*:*"

    fq = "+site_id:{}".format(toolkit.config.get("ckan.site_id"))

    response = solr.search(q=q, fq=fq)
    assert response.hits == 8

    index.clear_all()

    response = solr.search(q=q, fq=fq)
    assert response.hits == 0
