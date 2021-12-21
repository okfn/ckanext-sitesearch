import logging

from pysolr import SolrError

from ckan.plugins import toolkit
from ckan.lib.search.common import SearchError, SearchQueryError, make_connection
from ckan.lib.search.query import VALID_SOLR_PARAMETERS, solr_literal


log = logging.getLogger(__name__)


def query_organizations(query):

    if not query.get("fq_list"):
        query["fq_list"] = []
    query["fq_list"].append("entity_type:organization")

    return _run_query(query)


def query_groups(query):

    if not query.get("fq_list"):
        query["fq_list"] = []
    query["fq_list"].append("entity_type:group")

    return _run_query(query)


def query_users(query):

    if not query.get("fq_list"):
        query["fq_list"] = []
    query["fq_list"].append("entity_type:user")

    return _run_query(query)


def query_pages(query, permission_labels=None):

    if not query.get("fq_list"):
        query["fq_list"] = []
    query["fq_list"].append("entity_type:page")

    if not permission_labels:
        permission_labels = ["public"]

    return _run_query(query, permission_labels=permission_labels)


def _run_query(query, permission_labels=None):

    # Check that query keys are valid
    if not set(query.keys()) <= VALID_SOLR_PARAMETERS:
        invalid_params = [s for s in set(query.keys()) - VALID_SOLR_PARAMETERS]
        raise SearchQueryError("Invalid search parameters: {}".format(invalid_params))

    q = query.get("q")
    if not q or q in ('""', "''"):
        query["q"] = "*:*"

    if query["q"].startswith("{!"):
        raise SearchError("Local parameters are not supported.")

    fq = []
    if "fq" in query:
        fq.append(query["fq"])
    fq.extend(query.get("fq_list", []))

    # Show only results from this CKAN instance
    fq.append("+site_id:{}".format(solr_literal(toolkit.config.get("ckan.site_id"))))

    if permission_labels is not None:
        fq.append(
            "+permission_labels:(%s)"
            % " OR ".join(solr_literal(p) for p in permission_labels)
        )

    query["fq"] = fq

    query.setdefault("wt", "json")

    query.setdefault("df", "text")
    query.setdefault("q.op", "AND")

    conn = make_connection(decode_dates=False)
    log.debug("Sent Solr query: {}".format(query))
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
