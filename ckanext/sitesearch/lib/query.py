import logging

from pysolr import SolrError
from ckan.lib.search.common import SearchError, make_connection


log = logging.getLogger(__name__)


def query_organizations(query):

    if not query.get("fq"):
        query["fq"] = []
    query["fq"].append("entity_type:organization")

    return _run_query(query)


def query_groups(query):

    if not query.get("fq"):
        query["fq"] = []
    query["fq"].append("entity_type:group")

    return _run_query(query)


def query_users(query):

    if not query.get("fq"):
        query["fq"] = []
    query["fq"].append("entity_type:user")

    return _run_query(query)


def _run_query(query):

    q = query.get("q")
    if not q or q in ('""', "''"):
        query["q"] = "*:*"

    try:
        if query["q"].startswith("{!"):
            raise SearchError("Local parameters are not supported.")
    except KeyError:
        pass

    query.setdefault("wt", "json")

    query.setdefault("df", "text")
    query.setdefault("q.op", "AND")

    conn = make_connection(decode_dates=False)
    log.debug("Package query: %r" % query)
    try:
        solr_response = conn.search(**query)
    except SolrError as e:
        raise SearchError(
            "SOLR returned an error running query: %r Error: %r" % (query, e)
        )
    return {
        "count": solr_response.hits,
        "results": solr_response.docs,
    }
