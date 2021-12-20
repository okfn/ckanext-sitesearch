import sys
import logging

import click

from ckan import model
from ckan.plugins import toolkit

from ckanext.sitesearch.lib.index import index_organization

log = logging.getLogger(__name__)


def get_commands():
    return [sitesearch]


@click.group()
def sitesearch():
    """Search index utilities for CKAN entities."""
    pass


@sitesearch.command("rebuild")
@click.argument("entity_type")
def rebuild(entity_type):
    """Re-index all entitities of a particular type"""

    if entity_type in ("orgs", "org", "organizations", "organisations"):
        _rebuild_orgs()
    else:
        click.abort("Unknown entity type: {}".format(entity_type))


def _rebuild_orgs():
    # TODO:
    defer_commit = False

    org_ids = [
        r[0]
        for r in model.Session.query(model.Group.id)
        .filter(model.Group.is_organization == True)
        .filter(model.Group.state != "deleted")
        .all()
    ]

    total_orgs = len(org_ids)
    context = {"ignore_auth": True}
    for counter, org_id in enumerate(org_ids):
        sys.stdout.write(
            "\rIndexing organization {0}/{1}".format(counter + 1, total_orgs)
        )
        sys.stdout.flush()
        try:
            data_dict = toolkit.get_action("organization_show")(context, {"id": org_id})
            index_organization(data_dict, defer_commit)
        except Exception as e:
            log.error(u"Error while indexing organizaiton %s: %s" % (org_id, repr(e)))
            raise
