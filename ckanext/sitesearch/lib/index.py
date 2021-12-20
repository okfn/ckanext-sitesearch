import logging
import hashlib
import json
import socket

from pysolr import SolrError
import six
from six import text_type

from ckan.plugins import toolkit

from ckan.lib.search.common import SearchIndexError, make_connection
from ckan.lib.search.index import RESERVED_FIELDS, KEY_CHARS
from ckan.lib.navl.dictization_functions import MissingNullEncoder


DEFAULT_DEFER_COMMIT_VALUE = not toolkit.config.get("ckan.search.solr_commit", True)


log = logging.getLogger(__name__)


def _check_mandatory_fields(data_dict):

    if not data_dict.get("id"):
        raise ValueError("All indexed entities need an `id` field")
    site_id = toolkit.config.get("ckan.site_id")

    data_dict["site_id"] = site_id
    data_dict["index_id"] = hashlib.md5(
        six.b("%s%s" % (data_dict["id"], site_id))
    ).hexdigest()

    return data_dict


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


def _index_group_or_org(data_dict, defer_commit):

    data_dict = _check_mandatory_fields(data_dict)

    # Remove nested fields
    data_dict.pop("packages", None)
    data_dict.pop("users", None)
    data_dict.pop("groups", None)

    # Store full dict
    data_dict["validated_data_dict"] = json.dumps(data_dict, cls=MissingNullEncoder)

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
            value = " ".join(map(text_type, value))
        key = "".join([c for c in key if c in KEY_CHARS])
        data_dict["extras_" + key] = value
        if key not in index_fields:
            data_dict[key] = value
    data_dict.pop("extras", None)

    # TODO: created date

    # No permission labels, all group and org metadata is public

    # Send to Solr:
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


def commit(self):
    try:
        conn = make_connection()
        conn.commit(waitSearcher=False)
    except Exception as e:
        log.exception(e)
        raise SearchIndexError(e)
