import logging
import sys
import traceback

from ckan import model
from ckan.lib.search import rebuild as core_index_datasets
from ckan.plugins import plugin_loaded, toolkit
from ckanext.sitesearch.lib.index import (commit, index_group,
                                          index_organization,
                                          index_page,
                                          index_user)
from sqlalchemy.sql.expression import false, true

if plugin_loaded("pages"):
    from ckanext.pages.db import Page

log = logging.getLogger(__name__)


def rebuild_orgs(defer_commit, force, quiet, entity_id):
    print(entity_id)
    if entity_id:
        org = model.Group.get(entity_id)
        if not org:
            raise toolkit.ObjectNotFound("Organization not found: {}".format(entity_id))
        org_ids = [org.id]
    else:
        org_ids = [
            r[0]
            for r in model.Session.query(model.Group.id)
            .filter(model.Group.is_organization == true())
            .filter(model.Group.state != "deleted")
            .all()
        ]

    _rebuild_entities(
        org_ids, "organization", "organization_show", defer_commit, force, quiet
    )


def rebuild_groups(defer_commit, force, quiet, entity_id):

    if entity_id:
        group = model.Group.get(entity_id)
        if not group:
            raise toolkit.ObjectNotFound("Group not found: {}".format(entity_id))
        group_ids = [group.id]
    else:
        group_ids = [
            r[0]
            for r in model.Session.query(model.Group.id)
            .filter(model.Group.is_organization == false())
            .filter(model.Group.state != "deleted")
            .all()
        ]

    _rebuild_entities(group_ids, "group", "group_show", defer_commit, force, quiet)


def rebuild_users(defer_commit, force, quiet, entity_id):

    if entity_id:
        user = model.User.get(entity_id)
        if not user:
            raise toolkit.ObjectNotFound("User not found: {}".format(entity_id))
        user_ids = [user.id]
    else:
        user_ids = [
            r[0]
            for r in model.Session.query(model.User.id)
            .filter(model.User.state != "deleted")
            .all()
        ]

    _rebuild_entities(user_ids, "user", "user_show", defer_commit, force, quiet)


def rebuild_pages(defer_commit, force, quiet, entity_id):

    if not plugin_loaded("pages"):
        raise RuntimeError("The `pages` plugin needs to be enabled")

    if entity_id:
        page = Page.get(name=entity_id)
        if not page:
            raise toolkit.ObjectNotFound("Page not found: {}".format(entity_id))
        page_ids = [page.name]
    else:
        pages = Page.pages()
        page_ids = [r.name for r in pages]

    _rebuild_entities(
        page_ids,
        "page",
        "ckanext_pages_show",
        defer_commit,
        force,
        quiet,
        id_field="page",
    )


def rebuild_datasets(defer_commit, force, quiet, entity_id):

    if toolkit.check_ckan_version(min_version="2.10"):
        # CKAN >= 2.10 does not clear the index by default
        core_index_datasets(
            package_id=entity_id,
            force=force,
            quiet=quiet,
            defer_commit=defer_commit,
        )
    else:
        core_index_datasets(
            refresh=True,  # Ensure we are not clearing the index for other entities
            package_id=entity_id,
            force=force,
            quiet=quiet,
            defer_commit=defer_commit,
        )


indexers = {
    "organization": index_organization,
    "group": index_group,
    "user": index_user,
    "page": index_page,
}


def _rebuild_entities(
    entity_ids, entity_name, action_name, defer_commit, force, quiet, id_field="id"
):

    total_entities = len(entity_ids)
    context = {"ignore_auth": True}
    for counter, entity_id in enumerate(entity_ids):
        if not quiet:
            sys.stdout.write(
                "\rIndexing {} {}/{}".format(entity_name, counter + 1, total_entities)
            )
            sys.stdout.flush()
        try:
            data_dict = toolkit.get_action(action_name)(context, {id_field: entity_id})
            indexers[entity_name](data_dict, defer_commit)
        except Exception as e:
            log.error(
                "Error while indexing {} {}: {}".format(entity_name, entity_id, repr(e))
            )
            if force:
                log.exception(traceback.format_exc())
                continue
            else:
                raise

    if defer_commit:
        commit()
