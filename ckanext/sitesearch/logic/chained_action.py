from ckan import model
from ckan.plugins import toolkit

from ckanext.sitesearch.lib import index, rebuild


@toolkit.chained_action
def package_create(up_func, context, data_dict):

    data_dict = up_func(context, data_dict)

    owner_org = data_dict.get("owner_org", None)
    if owner_org:
        rebuild.rebuild_orgs(entity_id=owner_org)

    return data_dict


@toolkit.chained_action
def package_delete(up_func, context, data_dict):
    package_id = toolkit.get_or_bust(data_dict, "id")
    pkg = model.Package.get(package_id)
    if not pkg:
        raise toolkit.ObjectNotFound
    groups = pkg.get_groups()

    up_func(context, data_dict)

    for group in groups:
        if group.is_organization:
            rebuild.rebuild_orgs(entity_id=group.id)
        else:
            rebuild.rebuild_groups(entity_id=group.id)

    return data_dict


@toolkit.chained_action
def package_update(up_func, context, data_dict):
    package_id = toolkit.get_or_bust(data_dict, "id")
    pkg = model.Package.get(package_id)
    if not pkg:
        raise toolkit.ObjectNotFound
    old_org = pkg.owner_org

    data_dict = up_func(context, data_dict)
    new_org = data_dict.get("owner_org", None)

    if old_org != new_org:
        if old_org:
            rebuild.rebuild_orgs(entity_id=old_org)
        if new_org:
            rebuild.rebuild_orgs(entity_id=new_org)

    return data_dict


@toolkit.chained_action
def organization_create(up_func, context, data_dict):

    data_dict = up_func(context, data_dict)

    index.index_organization(data_dict)

    return data_dict


@toolkit.chained_action
def organization_update(up_func, context, data_dict):

    data_dict = up_func(context, data_dict)

    index.index_organization(data_dict)

    return data_dict


@toolkit.chained_action
def organization_delete(up_func, context, data_dict):

    up_func(context, data_dict)

    index.delete_organization(data_dict["id"])

    return data_dict


@toolkit.chained_action
def group_create(up_func, context, data_dict):

    data_dict = up_func(context, data_dict)

    index.index_group(data_dict)

    return data_dict


@toolkit.chained_action
def group_update(up_func, context, data_dict):

    data_dict = up_func(context, data_dict)

    index.index_group(data_dict)

    return data_dict


@toolkit.chained_action
def group_delete(up_func, context, data_dict):

    up_func(context, data_dict)

    index.delete_group(data_dict["id"])

    return data_dict


@toolkit.chained_action
def user_create(up_func, context, data_dict):

    data_dict = up_func(context, data_dict)

    index.index_user(data_dict)

    return data_dict


@toolkit.chained_action
def user_update(up_func, context, data_dict):

    data_dict = up_func(context, data_dict)

    index.index_user(data_dict)

    return data_dict


@toolkit.chained_action
def user_delete(up_func, context, data_dict):

    up_func(context, data_dict)

    index.delete_user(data_dict["id"])


@toolkit.chained_action
def pages_update(up_func, context, data_dict):

    up_func(context, data_dict)
    name = data_dict.get("page") or data_dict.get("name")
    page = toolkit.get_action("ckanext_pages_show")(context, {"page": name})
    index.index_page(page)


@toolkit.chained_action
def pages_delete(up_func, context, data_dict):

    up_func(context, data_dict)

    index.delete_page(data_dict["id"])


@toolkit.chained_action
def member_create(up_func, context, data_dict):

    result = up_func(context, data_dict)
    object_type = data_dict.get("object_type", None)

    if object_type and object_type == "package":
        rebuild.rebuild_groups(entity_id=data_dict["id"])

    return result
