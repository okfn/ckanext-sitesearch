import logging
import hashlib
from html import unescape
import json
import socket

from pysolr import SolrError

from ckan.plugins import toolkit, plugin_loaded

from ckan.lib.search.common import SearchIndexError, make_connection
from ckan.lib.search.index import RESERVED_FIELDS, KEY_CHARS
from ckan.lib.navl.dictization_functions import MissingNullEncoder

from ckanext.sitesearch.lib.utils import strip_html_tags


DEFAULT_DEFER_COMMIT_VALUE = not toolkit.config.get("ckan.search.solr_commit", True)


log = logging.getLogger(__name__)


def _check_mandatory_fields(data_dict):

    if not data_dict.get("id"):
        raise ValueError("All indexed entities need an `id` field")
    site_id = toolkit.config.get("ckan.site_id")

    data_dict["site_id"] = site_id
    data_dict["index_id"] = hashlib.md5(
        "{}{}".format(data_dict["id"], site_id).encode()
    ).hexdigest()

    return data_dict


def _format_date(value):
    # Solr 6 is picky with dates, wants a Z character at the end of ISO dates
    if not value[:-1] == "Z":
        value = value + "Z"
    return value


def index_group(data_dict, defer_commit=DEFAULT_DEFER_COMMIT_VALUE):

    if not data_dict:
        return

    data_dict["entity_type"] = "group"

    return _index_group_or_org(data_dict, defer_commit)


def index_organization(data_dict, defer_commit=DEFAULT_DEFER_COMMIT_VALUE):

    if not data_dict:
        return

    data_dict["entity_type"] = "organization"

    return _index_group_or_org(data_dict, defer_commit)


def index_user(data_dict, defer_commit=DEFAULT_DEFER_COMMIT_VALUE):

    if not data_dict:
        return

    data_dict = _check_mandatory_fields(data_dict)

    data_dict["entity_type"] = "user"

    # Make sure we don't index this
    data_dict.pop("apikey", None)

    # Store fields in the notes field so they get added to the default field
    data_dict["notes"] = " ".join(
        [
            data_dict.get("fullname", "") or "",
            data_dict.get("about", "") or "",
            data_dict.get("email", "") or "",
        ]
    )

    # Store full dict
    data_dict["validated_data_dict"] = json.dumps(data_dict, cls=MissingNullEncoder)

    # Created date
    data_dict["metadata_created"] = _format_date(data_dict["created"])

    return _send_to_solr(data_dict, defer_commit)


def _sanitize_text_for_search(text):

    # Remove HTML tags
    text = strip_html_tags(text)

    # Decode HTML entities
    text = unescape(text)

    # Replace line breaks
    for char in ("\r", "\n"):
        text = text.replace(char, "")

    # Replace tabs and spaces
    for char in ("\xa0", "\t"):
        text = text.replace(char, " ")

    return text


def index_page(data_dict, defer_commit=DEFAULT_DEFER_COMMIT_VALUE):

    if not data_dict:
        return

    if not plugin_loaded("pages"):
        raise RuntimeError("The `pages` plugin needs to be enabled")

    data_dict = _check_mandatory_fields(data_dict)

    data_dict["entity_type"] = "page"

    # Store full dict
    data_dict["validated_data_dict"] = json.dumps(data_dict, cls=MissingNullEncoder)

    # Created and modified dates
    # Note that publish_date will also be indexed as date
    data_dict["metadata_created"] = _format_date(data_dict["created"])
    data_dict["metadata_modified"] = _format_date(data_dict["modified"])
    if data_dict.get("publish_date"):
        data_dict["publish_date"] = _format_date(data_dict["publish_date"])

    # Index content (minus HTML tags) in the notes field so it gets copied to
    # the catch-all `text` field
    data_dict["notes"] = _sanitize_text_for_search(data_dict["content"])

    # Drop the content field otherwise will get stored in the catch-all `string` field,
    # which has a length limit which is easy to reach with a page content
    data_dict.pop("content", None)

    # Add string title field for sorting
    data_dict["title_string"] = data_dict.get("title")

    # Permissions
    # The intent is to mimic ckanext-pages behaviour:
    # * If not org_id and private=True -> sysadmins only
    # * If org_id and private=True -> org/groups admins and sysadmins only
    # * All other cases -> public
    # See ckanext-pages auth.py module
    from ckanext.pages.db import Page

    labels = []
    page = Page.get(name=data_dict["name"], group_id=data_dict.get("group_id"))
    if not page:
        raise toolkit.ObjectNotFound("Page not found: {}".format(data_dict["name"]))
    if page.private:
        labels.append("sysadmin")
        if page.group_id:
            labels.append("group_id-{}".format(page.group_id))
    else:
        labels.append("public")

    data_dict["permission_labels"] = labels

    return _send_to_solr(data_dict, defer_commit)


def _index_group_or_org(data_dict, defer_commit):

    data_dict = _check_mandatory_fields(data_dict)

    # Remove nested fields
    data_dict.pop("packages", None)
    data_dict.pop("users", None)
    data_dict.pop("groups", None)

    # Store full dict
    data_dict["validated_data_dict"] = json.dumps(data_dict, cls=MissingNullEncoder)

    # Store description in the notes field so it gets added to the default field
    data_dict["notes"] = data_dict["description"]

    # Add string title field for sorting
    data_dict["title_string"] = data_dict.get("title")

    # Handle extras for each extra, add an `extra_{name}` text field
    # and a string `{name}` field (if not already in the schema)

    index_fields = RESERVED_FIELDS + list(data_dict.keys())

    # Include the extras in the main namespace
    extras = data_dict.get("extras", [])
    for extra in extras:
        key, value = extra["key"], extra["value"]
        if isinstance(value, (tuple, list)):
            value = " ".join(value)
        key = "".join([c for c in key if c in KEY_CHARS])
        data_dict["extras_" + key] = value
        if key not in index_fields:
            data_dict[key] = value
    data_dict.pop("extras", None)

    # Created date
    data_dict["metadata_created"] = _format_date(data_dict["created"])

    # No permission labels, all group and org metadata is public

    return _send_to_solr(data_dict, defer_commit)


def _send_to_solr(data_dict, defer_commit):

    commit = not defer_commit
    try:
        conn = make_connection()
        conn.add(docs=[data_dict], commit=commit)
    except SolrError as e:
        msg = "Solr returned an error: {0}".format(
            e.args[0][:1000]  # limit huge responses
        )
        raise SearchIndexError(msg)
    except socket.error as e:
        err = "Could not connect to Solr using {0}: {1}".format(conn.url, str(e))
        log.error(err)
        raise SearchIndexError(err)

    commit_debug_msg = "Not committed yet" if defer_commit else "Committed"
    log.debug(
        "Updated index for {} [{}]".format(data_dict.get("name"), commit_debug_msg)
    )


def commit():
    try:
        conn = make_connection()
        conn.commit(waitSearcher=False)
        log.debug("Commited changes on the Solr index")
    except SolrError as e:
        log.exception(e)
        raise SearchIndexError(e)


def delete_group(id, defer_commit=DEFAULT_DEFER_COMMIT_VALUE):
    return _delete("group", id, defer_commit)


def delete_organization(id, defer_commit=DEFAULT_DEFER_COMMIT_VALUE):
    return _delete("organization", id, defer_commit)


def delete_user(id, defer_commit=DEFAULT_DEFER_COMMIT_VALUE):
    return _delete("user", id, defer_commit)


def _delete(entity_type, entity_id, defer_commit):

    commit = not defer_commit

    query = []
    query.append("+entity_type:{}".format(entity_type))

    query.append(
        '+(id:"{entity_id}" OR name:"{entity_id}")'.format(entity_id=entity_id)
    )
    query.append('+site_id:"{}"'.format(toolkit.config.get("ckan.site_id")))

    query = " AND ".join(query)
    try:
        conn = make_connection()
        conn.delete(q=query, commit=commit)
        log.debug("Deleted {} {} the Solr index".format(entity_type, entity_id))
    except SolrError as e:
        log.exception(e)
        raise SearchIndexError(e)


def clear_organizations(defer_commit=DEFAULT_DEFER_COMMIT_VALUE):
    _clear(entity_type="organization", defer_commit=defer_commit)
    log.debug("Deleted all organizations from the Solr index")


def clear_groups(defer_commit=DEFAULT_DEFER_COMMIT_VALUE):
    _clear(entity_type="group", defer_commit=defer_commit)
    log.debug("Deleted all groups from the Solr index")


def clear_users(defer_commit=DEFAULT_DEFER_COMMIT_VALUE):
    _clear(entity_type="user", defer_commit=defer_commit)
    log.debug("Deleted all users from the Solr index")


def clear_all(defer_commit=DEFAULT_DEFER_COMMIT_VALUE):
    _clear(keep_datasets=False, defer_commit=defer_commit)
    log.debug("Deleted all entities from the Solr index")


def _clear(
    entity_type=None, keep_datasets=True, defer_commit=DEFAULT_DEFER_COMMIT_VALUE
):
    commit = not defer_commit

    query = []

    if entity_type:
        query.append("+entity_type:{}".format(entity_type))

    if keep_datasets:
        query.append("-entity_type:package")

    query.append("+site_id:{}".format(toolkit.config.get("ckan.site_id")))

    query = " AND ".join(query)
    try:
        conn = make_connection()
        conn.delete(q=query, commit=commit)
    except SolrError as e:
        log.exception(e)
        raise SearchIndexError(e)
