import datetime
from unittest import mock

import pytest

from ckan import model
from ckan.plugins import toolkit
from ckan.lib.search import SearchQueryError, clear_all as reset_index
from ckan.tests import factories, helpers

from ckanext.sitesearch.lib.index import index_page
from ckanext.sitesearch.logic.action import parse_search_params
from ckanext.pages import db as pages_db

call_action = helpers.call_action


@pytest.fixture
def pages_setup():
    pages_db.init_db()


@pytest.fixture(scope="class")
def group_search_fixtures():
    factories.Group(
        name="test_group_1",
        title="My Group 1",
        description="Witness this great group",
    )

    factories.Organization(
        name="test_org_1",
        title="My organization 1",
        description="Behold this great organization",
        extras=[
            {"key": "extra_org_common", "value": "pear"},
            {"key": "extra_org_1", "value": 4},
        ],
    )

    factories.Organization(
        name="test_org_2",
        title="My organization 2",
        description="Marvel at this great organization",
        extras=[
            {"key": "extra_org_common", "value": "peach"},
            {"key": "extra_org_2", "value": 6},
        ],
    )
    yield
    helpers.reset_db()
    reset_index()


@pytest.mark.usefixtures("group_search_fixtures")
class TestGroupOrOrgSearch(object):
    def test_group_search_no_params(self):
        result = call_action("group_search")

        assert result["count"] == 1
        assert result["results"][0]["name"] == "test_group_1"

    def test_organization_search_invalid_params(self):
        with pytest.raises(toolkit.ValidationError):
            call_action("organization_search", rows="invalid")

    def test_organization_search_bad_params(self):
        with pytest.raises(SearchQueryError):
            call_action("organization_search", some="param")

    def test_organization_search_no_params(self):
        result = call_action("organization_search")

        assert result["count"] == 2

    def test_organization_search_free_search(self):
        result = call_action("organization_search", q="organization")

        assert result["count"] == 2

    def test_organization_search_free_search_description(self):
        result = call_action("organization_search", q="behold")

        assert result["count"] == 1
        assert result["results"][0]["name"] == "test_org_1"

    def test_organization_search_free_search_extras(self):
        result = call_action("organization_search", q="pear")

        assert result["count"] == 1
        assert result["results"][0]["name"] == "test_org_1"

    def test_organization_search_wildcard(self):
        result = call_action("organization_search", q="pea*")

        assert result["count"] == 2

    def test_organization_search_or(self):
        result = call_action("organization_search", q="pear OR peach")

        assert result["count"] == 2

    def test_organization_search_field(self):
        result = call_action("organization_search", q="name:test_org_1")

        assert result["count"] == 1
        assert result["results"][0]["name"] == "test_org_1"

    def test_organization_search_default_sort(self):
        result = call_action("organization_search")

        assert result["count"] == 2

        assert result["results"][0]["title"] == "My organization 1"
        assert result["results"][1]["title"] == "My organization 2"

    def test_organization_search_rows(self):
        result = call_action("organization_search", rows=1, start=1)

        assert result["count"] == 2
        assert len(result["results"]) == 1

        assert result["results"][0]["title"] == "My organization 2"

    def test_organization_search_custom_sort(self):
        result = call_action("organization_search", sort="extra_org_common asc")

        assert result["count"] == 2

        assert [
            e["value"]
            for e in result["results"][0]["extras"]
            if e["key"] == "extra_org_common"
        ][0] == "peach"

        assert [
            e["value"]
            for e in result["results"][1]["extras"]
            if e["key"] == "extra_org_common"
        ][0] == "pear"

    def test_organization_facets(self):

        params = {
            "facet": "on",
            "facet.field": ["extra_org_common"],
        }

        result = call_action("organization_search", **params)

        assert (
            result["search_facets"]["extra_org_common"]["title"] == "extra_org_common"
        )

        assert (
            result["search_facets"]["extra_org_common"]["items"][0]["name"] == "peach"
        )
        assert result["search_facets"]["extra_org_common"]["items"][0]["count"] == 1
        assert result["search_facets"]["extra_org_common"]["items"][1]["name"] == "pear"
        assert result["search_facets"]["extra_org_common"]["items"][1]["count"] == 1


@pytest.fixture(scope="class")
def user_search_fixtures():
    factories.User(
        name="test_user_1",
        fullname="My user 1",
        email="user1@example.com",
        about="Behold this great user",
    )

    factories.User(
        name="test_user_2",
        fullname="My user 2",
        email="user2@example.com",
        about="Witness this great user",
    )
    yield
    helpers.reset_db()
    reset_index()


@pytest.mark.usefixtures("pages_setup", "user_search_fixtures")
class TestUserSearch(object):
    def test_user_search_no_params(self):
        result = call_action("user_search")

        assert result["count"] == 2

    def test_user_search_invalid_params(self):
        with pytest.raises(toolkit.ValidationError):
            call_action("user_search", rows="invalid")

    def test_user_search_bad_params(self):
        with pytest.raises(SearchQueryError):
            call_action("user_search", some="param")

    def test_user_search_free_search(self):
        result = call_action("user_search", q="user")

        assert result["count"] == 2

    def test_user_search_free_search_about(self):
        result = call_action("user_search", q="behold")

        assert result["count"] == 1
        assert result["results"][0]["name"] == "test_user_1"

    def test_user_search_wildcard(self):
        result = call_action("user_search", q="My user *")

        assert result["count"] == 2

    def test_user_search_or(self):
        result = call_action("user_search", q="behold OR witness")

        assert result["count"] == 2

    def test_user_search_field(self):
        result = call_action("user_search", q="email:user1@example.com")

        assert result["count"] == 1
        assert result["results"][0]["name"] == "test_user_1"

    def test_user_search_default_sort(self):
        result = call_action("user_search")

        assert result["count"] == 2

        assert result["results"][0]["fullname"] == "My user 1"
        assert result["results"][1]["fullname"] == "My user 2"

    def test_user_search_custom_sort(self):
        result = call_action("user_search", sort="email desc")

        assert result["count"] == 2

        assert result["results"][0]["fullname"] == "My user 2"
        assert result["results"][1]["fullname"] == "My user 1"

    def test_user_search_rows(self):
        result = call_action("user_search", rows=1, start=1)

        assert result["count"] == 2
        assert len(result["results"]) == 1

        assert result["results"][0]["fullname"] == "My user 2"

    def test_user_facets(self):

        params = {
            "facet": "on",
            "facet.field": ["email"],
        }

        result = call_action("user_search", **params)

        assert result["search_facets"]["email"]["title"] == "email"

        assert (
            result["search_facets"]["email"]["items"][0]["name"] == "user1@example.com"
        )
        assert result["search_facets"]["email"]["items"][0]["count"] == 1
        assert (
            result["search_facets"]["email"]["items"][1]["name"] == "user2@example.com"
        )
        assert result["search_facets"]["email"]["items"][1]["count"] == 1


@pytest.mark.usefixtures("pages_setup")
class TestPageSearch(object):
    @classmethod
    def _create_pages(cls, sysadmin=None):
        if not sysadmin:
            sysadmin = factories.Sysadmin()
        context = {
            "user": sysadmin["name"],
            "auth_user_obj": model.User.get(sysadmin["id"]),
        }
        for page_name in ("test_page_1", "test_page_2"):
            page = toolkit.get_action("ckanext_pages_show")(
                context, {"page": page_name}
            )
            if page:
                index_page(page)
        if page:
            # Pages already exist
            return

        call_action(
            "ckanext_pages_update",
            name="test_page_1",
            title="My page 1",
            publish_date=datetime.datetime.utcnow().isoformat(),
            content="""<h1>Some page 1</h1>
                <b>Behold</b> this great page.
                """,
            private=False,
            page_type="page",
            context=context,
        )

        call_action(
            "ckanext_pages_update",
            name="test_page_2",
            title="My page 2",
            publish_date=datetime.datetime.utcnow().isoformat(),
            content="""<h1>Some page 2</h1>
                <b>Witness</b> this great page.
                """,
            private=False,
            page_type="page",
            context=context,
        )

        call_action(
            "ckanext_pages_update",
            name="test_page_3",
            title="My page 3",
            publish_date=datetime.datetime.utcnow().isoformat(),
            content="""<h1>Some page 3</h1>
                <b>Marvel</b> at this great private page.
                """,
            private=True,
            page_type="page",
            context=context,
        )

    @classmethod
    def teardown_class(cls):
        helpers.reset_db()
        reset_index()

    def test_page_search_invalid_params(self):
        with pytest.raises(toolkit.ValidationError):
            call_action("page_search", rows="invalid")

    def test_page_search_bad_params(self):
        with pytest.raises(SearchQueryError):
            call_action("page_search", some="param")

    def test_page_search_no_params(self):

        self._create_pages()

        sysadmin = factories.Sysadmin()
        context = {
            "user": sysadmin["name"],
            "auth_user_obj": model.User.get(sysadmin["id"]),
        }

        # Anon query, only public pages
        result = call_action("page_search")

        assert result["count"] == 2

        # Admin query, all pages returned
        result = call_action("page_search", context=context)
        assert result["count"] == 3

    def test_page_search_free_search(self):

        self._create_pages()
        result = call_action("page_search", q="some")

        assert result["count"] == 2

    def test_page_search_free_search_content(self):

        self._create_pages()
        result = call_action("page_search", q="witness")

        assert result["count"] == 1
        assert result["results"][0]["name"] == "test_page_2"

    def test_page_search_html_tags_not_indexed(self):

        self._create_pages()
        result = call_action("page_search", q="<b>")

        assert result["count"] == 0

    def test_page_search_wildcard(self):

        self._create_pages()
        result = call_action("page_search", q="My page *")

        assert result["count"] == 2

    def test_page_search_wildcard_html_tags(self):

        self._create_pages()
        result = call_action("page_search", q="Behold*")

        assert result["count"] == 1

    def test_page_search_or(self):

        self._create_pages()
        result = call_action("page_search", q="behold OR witness")

        assert result["count"] == 2

    def test_page_search_field(self):

        self._create_pages()
        result = call_action("page_search", q='title:"My page 2"')

        assert result["count"] == 1
        assert result["results"][0]["name"] == "test_page_2"

    def test_page_search_default_sort(self):

        self._create_pages()
        result = call_action("page_search")

        assert result["count"] == 2

        # Default sort is published_date desc, metadata_modified desc
        assert result["results"][0]["title"] == "My page 2"
        assert result["results"][1]["title"] == "My page 1"

    def test_page_search_custom_sort(self):

        self._create_pages()
        result = call_action("page_search", sort="title asc")

        assert result["count"] == 2

        assert result["results"][0]["title"] == "My page 1"
        assert result["results"][1]["title"] == "My page 2"

    def test_page_search_rows(self):

        self._create_pages()
        result = call_action("page_search", rows=1, start=1)

        assert result["count"] == 2
        assert len(result["results"]) == 1

        assert result["results"][0]["title"] == "My page 1"

    def test_page_sort_by_title(self):

        self._create_pages()

        result = call_action("page_search", sort="title_string asc")

        assert [p["title"] for p in result["results"]] == [
            "My page 1",
            "My page 2",
        ]

        result = call_action("page_search", sort="title_string desc")

        assert [p["title"] for p in result["results"]] == [
            "My page 2",
            "My page 1",
        ]

    def test_page_facets(self):

        sysadmin = factories.Sysadmin()
        context = {
            "user": sysadmin["name"],
            "auth_user_obj": model.User.get(sysadmin["id"]),
        }

        self._create_pages()
        params = {
            "facet": "on",
            "facet.field": ["private"],
        }

        result = call_action("page_search", context=context, **params)

        assert result["search_facets"]["private"]["title"] == "private"

        assert result["search_facets"]["private"]["items"][0]["name"] == "false"
        assert result["search_facets"]["private"]["items"][0]["count"] == 2
        assert result["search_facets"]["private"]["items"][1]["name"] == "true"
        assert result["search_facets"]["private"]["items"][1]["count"] == 1


@pytest.fixture()
def site_search_fixtures():

    factories.Group(
        name="test_group_1",
        title="My Group 1",
        description="Witness this great group",
    )

    org1 = factories.Organization(
        name="test_org_1",
        title="My organization 1",
        description="Behold this great organization",
        extras=[
            {"key": "extra_org_common", "value": "pear"},
            {"key": "extra_org_1", "value": 4},
        ],
    )

    org2 = factories.Organization(
        name="test_org_2",
        title="My organization 2",
        description="Marvel at this great organization",
        extras=[
            {"key": "extra_org_common", "value": "peach"},
            {"key": "extra_org_2", "value": 6},
        ],
    )

    factories.Dataset(
        name="test_dataset_1",
        notes="Behold this great dataset",
        owner_org=org1["id"],
        license_id="cc-by",
    )

    factories.Dataset(
        name="test_dataset_2",
        notes="Witness this great dataset",
        owner_org=org2["id"],
        license_id="odc-odbl",
    )

    factories.User(
        name="test_user_1",
        fullname="My user 1",
        email="user1@example.com",
        about="Behold this great user",
    )

    sysadmin = factories.Sysadmin(
        name="test_user_2",
        fullname="My user 2",
        email="user2@example.com",
        about="Witness this great user",
    )

    TestPageSearch._create_pages(sysadmin=sysadmin)
    yield
    helpers.reset_db()
    reset_index()


@pytest.mark.usefixtures(
    "pages_setup", "clean_db", "clean_index", "site_search_fixtures"
)
class TestSiteSearch(object):
    def test_site_search_no_params(self):
        result = call_action("site_search")

        assert result["datasets"]["count"] == 2
        assert result["groups"]["count"] == 1
        assert result["organizations"]["count"] == 2
        assert result["users"]["count"] == 2
        assert result["pages"]["count"] == 2

    def test_site_search_invalid_params(self):
        with pytest.raises(toolkit.ValidationError):
            call_action("site_search", rows="invalid")

    def test_site_search_bad_params(self):
        with pytest.raises(SearchQueryError):
            call_action("site_search", some="param")

    def test_site_search_free_search(self):
        result = call_action("site_search", q="behold")

        assert result["datasets"]["count"] == 1
        assert result["groups"]["count"] == 0
        assert result["organizations"]["count"] == 1
        assert result["users"]["count"] == 1
        assert result["pages"]["count"] == 1

    def test_site_search_namespace_params(self):

        with mock.patch("ckanext.sitesearch.logic.action.toolkit.get_action") as ga:

            params = {
                "q": "behold",
                "datasets.rows": 5,
                "pages.fq": "page_type:page",
            }

            call_action("site_search", **params)

            assert len(ga().call_args_list) == 5

            # package_search
            assert ga().call_args_list[0][0][1] == {"rows": 5, "q": "behold"}

            # group/organization/user_search
            for i in (1, 2, 3):
                assert ga().call_args_list[i][0][1] == {"q": "behold"}

            # pages_search
            assert ga().call_args_list[4][0][1] == {
                "fq": "page_type:page",
                "q": "behold",
            }

    def test_site_search_namespace_params_for_facets(self):

        sysadmin = factories.Sysadmin(email="sysadmin1@example.com")
        context = {
            "user": sysadmin["name"],
            "auth_user_obj": model.User.get(sysadmin["id"]),
        }

        params = {
            "datasets.facet.field": ["license_id"],
            "users.facet.field": ["email"],
            "facet": "on",
            "facet.mincount": 1,
        }

        result = call_action("site_search", context=context, **params)

        assert (
            result["datasets"]["search_facets"]["license_id"]["items"][0]["name"]
            == "odc-odbl"
        )
        assert (
            result["datasets"]["search_facets"]["license_id"]["items"][0]["count"] == 1
        )
        assert (
            result["datasets"]["search_facets"]["license_id"]["items"][1]["name"]
            == "cc-by"
        )
        assert (
            result["datasets"]["search_facets"]["license_id"]["items"][1]["count"] == 1
        )

        assert (
            result["users"]["search_facets"]["email"]["items"][0]["name"]
            == "sysadmin1@example.com"
        )
        assert result["users"]["search_facets"]["email"]["items"][0]["count"] == 1

        assert (
            result["users"]["search_facets"]["email"]["items"][1]["name"]
            == "user1@example.com"
        )
        assert result["users"]["search_facets"]["email"]["items"][1]["count"] == 1
        assert (
            result["users"]["search_facets"]["email"]["items"][2]["name"]
            == "user2@example.com"
        )
        assert result["users"]["search_facets"]["email"]["items"][2]["count"] == 1

        assert (
            result["organizations"]["search_facets"]
            == result["groups"]["search_facets"]
            == result["pages"]["search_facets"]
            == {}
        )

    def test_site_search_not_auth(self):

        user = factories.User()
        context = {"user": user["name"], "ignore_auth": False}

        result = call_action("site_search", context=context)

        assert "users" not in result


class TestParseSearchParams(object):
    def test_parse_params(self):

        data_dict = {
            "datasets.start": 0,
            "datasets.rows": 20,
            "datasets.facet.field": ["tags", "groups"],
            "groups.facet.field": ["type"],
            "facet.limit": 10,
            "q": "test",
            "fq": "state:active",
        }

        search_params = parse_search_params(data_dict)

        assert sorted(search_params.keys()) == [
            "datasets",
            "groups",
            "organizations",
            "users",
        ]

        assert search_params["datasets"] == {
            "start": 0,
            "rows": 20,
            "facet.field": ["tags", "groups"],
            "facet.limit": 10,
            "q": "test",
            "fq": "state:active",
        }

        assert search_params["groups"] == {
            "facet.field": ["type"],
            "facet.limit": 10,
            "q": "test",
            "fq": "state:active",
        }

        assert (
            search_params["organizations"]
            == search_params["users"]
            == {
                "q": "test",
                "facet.limit": 10,
                "fq": "state:active",
            }
        )

    def test_parse_params_overrides(self):

        data_dict = {
            "datasets.fq": "state:pending",
            "fq": "state:active",
        }

        search_params = parse_search_params(data_dict)

        assert search_params["datasets"]["fq"] == "state:pending"
        for key in ("groups", "organizations", "users"):
            assert search_params[key]["fq"] == "state:active"

    def test_parse_params_extra_searches(self):

        data_dict = {
            "datasets.start": 0,
            "groups.facet.field": ["type"],
            "news.fq": "type:page",
            "facet.limit": 10,
            "q": "test",
            "fq": "state:active",
        }

        search_params = parse_search_params(
            data_dict, searches=["datasets", "groups", "news"]
        )

        assert sorted(search_params.keys()) == [
            "datasets",
            "groups",
            "news",
        ]

        assert search_params["news"] == {
            "fq": "type:page",
            "facet.limit": 10,
            "q": "test",
        }


@pytest.mark.usefixtures("clean_db", "clean_index")
class TestPackageSearch(object):
    @pytest.mark.ckan_config("ckan.auth.create_unowned_dataset", True)
    def test_package_search_returns_only_datasets(self):

        factories.User()

        factories.Group()

        factories.Dataset()
        factories.Dataset()
        factories.Dataset(type="custom_dataset")

        context = {"ignore_auth": False}

        result = toolkit.get_action("package_search")(context, {})

        assert result["count"] == 3

        for item in result["results"]:
            assert item["type"] in ("dataset", "custom_dataset")
