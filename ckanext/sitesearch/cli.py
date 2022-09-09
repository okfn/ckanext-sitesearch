import logging

import click
from ckan.plugins import toolkit
from ckanext.sitesearch.lib.rebuild import (
    rebuild_datasets,
    rebuild_groups,
    rebuild_orgs,
    rebuild_pages,
    rebuild_users,
)

log = logging.getLogger(__name__)


def get_commands():
    return [sitesearch]


@click.group()
def sitesearch():
    """Search index utilities for CKAN entities."""
    pass


@sitesearch.command("rebuild")
@click.argument("entity_type")
@click.argument("entity_id", required=False)
@click.option(
    "-e",
    "--commit-each",
    is_flag=True,
    help="Perform a commit after indexing each dataset. This"
    "ensures that changes are immediately available on the"
    "search, but slows significantly the process. Default"
    "is false.",
)
@click.option(
    "-i", "--force", is_flag=True, help="Ignore exceptions when rebuilding the index"
)
@click.option(
    "-q", "--quiet", help="Do not output index rebuild progress", is_flag=True
)
def rebuild(entity_type, commit_each, force, quiet, entity_id=None):
    """Re-index all entitities of a particular type"""

    defer_commit = not commit_each

    if entity_type in ("orgs", "org", "organizations", "organisations"):
        rebuild_orgs(defer_commit, force, quiet, entity_id)
    elif entity_type in ("groups", "group"):
        rebuild_groups(defer_commit, force, quiet, entity_id)
    elif entity_type in ("users", "user"):
        rebuild_users(defer_commit, force, quiet, entity_id)
    elif entity_type in ("pages", "page"):
        rebuild_pages(defer_commit, force, quiet, entity_id)
    elif entity_type in ("dataset", "datasets", "package", "packages"):
        rebuild_datasets(defer_commit, force, quiet, entity_id)
    else:
        toolkit.error_shout("Unknown entity type: {}".format(entity_type))
        raise click.Abort()
