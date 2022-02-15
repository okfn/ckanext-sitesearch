import datetime

import pytest

from ckan import model
from ckan.plugins import toolkit
from ckan.lib.search import SearchQueryError, clear_all as reset_index
from ckan.tests import factories, helpers

from ckanext.sitesearch.lib.index import index_page
from ckanext.pages import db

call_action = helpers.call_action


@pytest.fixture
def pages_setup():
    db.init_db()


class TestGroupOrOrgSearch(object):
    @classmethod
    def setup_class(cls):

        cls.group = factories.Group(
            name="test_group_1",
            title="My Group 1",
            description="Witness this great group",
        )

        cls.org1 = factories.Organization(
            name="test_org_1",
            title="My organization 1",
            description="Behold this great organization",
            extras=[
                {"key": "extra_org_common", "value": "pear"},
                {"key": "extra_org_1", "value": 4},
            ],
        )

        cls.org2 = factories.Organization(
            name="test_org_2",
            title="My organization 2",
            description="Marvel at this great organization",
            extras=[
                {"key": "extra_org_common", "value": "peach"},
                {"key": "extra_org_2", "value": 6},
            ],
        )

    @classmethod
    def teardown_class(cls):
        helpers.reset_db()
        reset_index()

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


@pytest.mark.usefixtures("pages_setup")
class TestUserSearch(object):
    @classmethod
    def setup_class(cls):

        cls.user1 = factories.User(
            name="test_user_1",
            fullname="My user 1",
            email="user1@example.com",
            about="Behold this great user",
        )

        cls.user2 = factories.User(
            name="test_user_2",
            fullname="My user 2",
            email="user2@example.com",
            about="Witness this great user",
        )

    @classmethod
    def teardown_class(cls):
        helpers.reset_db()
        reset_index()

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


@pytest.mark.usefixtures("pages_setup")
class TestPageSearch(object):
    @classmethod
    def _create_pages(cls):
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


@pytest.mark.usefixtures("pages_setup", "clean_db", "clean_index")
class TestSiteSearch(object):
    def setup(self):

        self.group = factories.Group(
            name="test_group_1",
            title="My Group 1",
            description="Witness this great group",
        )

        self.org1 = factories.Organization(
            name="test_org_1",
            title="My organization 1",
            description="Behold this great organization",
            extras=[
                {"key": "extra_org_common", "value": "pear"},
                {"key": "extra_org_1", "value": 4},
            ],
        )

        self.org2 = factories.Organization(
            name="test_org_2",
            title="My organization 2",
            description="Marvel at this great organization",
            extras=[
                {"key": "extra_org_common", "value": "peach"},
                {"key": "extra_org_2", "value": 6},
            ],
        )

        self.dataset1 = factories.Dataset(
            name="test_dataset_1",
            notes="Behold this great dataset",
            owner_org=self.org1["id"],
        )

        self.dataset2 = factories.Dataset(
            name="test_dataset_2",
            notes="Witness this great dataset",
            owner_org=self.org2["id"],
        )

        self.user1 = factories.User(
            name="test_user_1",
            fullname="My user 1",
            email="user1@example.com",
            about="Behold this great user",
        )

        self.user2 = factories.User(
            name="test_user_2",
            fullname="My user 2",
            email="user2@example.com",
            about="Witness this great user",
        )

        TestPageSearch._create_pages()

    @classmethod
    def teardown_class(cls):
        helpers.reset_db()
        reset_index()

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

    def test_site_search_not_auth(self):

        user = factories.User()
        context = {"user": user["name"], "ignore_auth": False}

        result = call_action("site_search", context=context)

        assert "users" not in result


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
