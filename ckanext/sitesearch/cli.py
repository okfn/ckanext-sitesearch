import sys
import logging

import click
from sqlalchemy.sql.expression import true, false

from ckan import model
from ckan.plugins import toolkit

from ckanext.sitesearch.lib.index import index_organization, index_group, index_user

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
    elif entity_type in ("groups", "group"):
        _rebuild_groups()
    elif entity_type in ("users", "user"):
        _rebuild_users()
    else:
        toolkit.error_shout("Unknown entity type: {}".format(entity_type))


def _rebuild_orgs():
    # TODO:
    defer_commit = False

    org_ids = [
        r[0]
        for r in model.Session.query(model.Group.id)
        .filter(model.Group.is_organization == true())
        .filter(model.Group.state != "deleted")
        .all()
    ]

    _rebuild_entities(org_ids, "organization", "organization_show", defer_commit)


def _rebuild_groups():
    # TODO:
    defer_commit = False

    group_ids = [
        r[0]
        for r in model.Session.query(model.Group.id)
        .filter(model.Group.is_organization == false())
        .filter(model.Group.state != "deleted")
        .all()
    ]

    _rebuild_entities(group_ids, "group", "group_show", defer_commit)


def _rebuild_users():
    # TODO:
    defer_commit = False

    user_ids = [
        r[0]
        for r in model.Session.query(model.User.id)
        .filter(model.User.state != "deleted")
        .all()
    ]

    _rebuild_entities(user_ids, "user", "user_show", defer_commit)


indexers = {
    "organization": index_organization,
    "group": index_group,
    "user": index_user,
}


def _rebuild_entities(entity_ids, entity_name, action_name, defer_commit):

    total_entities = len(entity_ids)
    context = {"ignore_auth": True}
    for counter, entity_id in enumerate(entity_ids):
        sys.stdout.write(
            "\rIndexing {} {}/{}".format(entity_name, counter + 1, total_entities)
        )
        sys.stdout.flush()
        try:
            data_dict = toolkit.get_action(action_name)(context, {"id": entity_id})
            indexers[entity_name](data_dict, defer_commit)
        except Exception as e:
            log.error(
                "Error while indexing {} {}: {}".format(entity_name, entity_id, repr(e))
            )
            raise
