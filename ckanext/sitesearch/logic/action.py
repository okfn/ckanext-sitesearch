import json

from ckan.plugins import toolkit

from ckanext.sitesearch.logic.schema import default_search_schema
from ckanext.sitesearch.lib import query


queriers = {
    "organization": query.query_organizations,
    "group": query.query_groups,
    "user": query.query_users,
    "page": query.query_pages,
}


@toolkit.side_effect_free
def organization_search(context, data_dict):

    toolkit.check_access("organization_search", context, data_dict)

    return _group_or_org_search("organization", context, data_dict)


@toolkit.side_effect_free
def group_search(context, data_dict):

    toolkit.check_access("group_search", context, data_dict)

    return _group_or_org_search("group", context, data_dict)


def _group_or_org_search(entity_name, context, data_dict):
    schema = context.get("schema") or default_search_schema()

    data_dict, errors = toolkit.navl_validate(data_dict, schema, context)

    if errors:
        raise toolkit.ValidationError(errors)

    if not data_dict.get("sort"):
        data_dict["sort"] = "title asc"

    return _perform_search(entity_name, context, data_dict)


@toolkit.side_effect_free
def user_search(context, data_dict):

    toolkit.check_access("user_search", context, data_dict)

    schema = context.get("schema") or default_search_schema()

    data_dict, errors = toolkit.navl_validate(data_dict, schema, context)
    if errors:
        raise toolkit.ValidationError(errors)

    if not data_dict.get("sort"):
        data_dict["sort"] = "fullname asc, name asc"

    return _perform_search("user", context, data_dict)


@toolkit.side_effect_free
def page_search(context, data_dict):

    toolkit.check_access("page_search", context, data_dict)

    schema = context.get("schema") or default_search_schema()

    data_dict, errors = toolkit.navl_validate(data_dict, schema, context)
    if errors:
        raise toolkit.ValidationError(errors)

    if not data_dict.get("sort"):
        data_dict["sort"] = "publish_date desc, metadata_modified desc"

    permission_labels = _get_user_page_labels(context["auth_user_obj"])

    return _perform_search(
        "page", context, data_dict, permission_labels=permission_labels
    )


@toolkit.side_effect_free
def site_search(context, data_dict):

    toolkit.check_access("site_search", context, data_dict)

    out = {}
    searches = [
        ("datasets", "package_search"),
        ("organizations", "organization_search"),
        ("groups", "group_search"),
        ("users", "user_search"),
        ("pages", "page_search"),
    ]
    for search in searches:
        name, action_name = search
        try:
            toolkit.check_access(action_name, context, data_dict)
            out[name] = toolkit.get_action(action_name)(context, data_dict)
        except toolkit.NotAuthorized:
            pass

    return out


def _perform_search(entity_name, context, data_dict, permission_labels=None):

    data_dict.update(data_dict.get('__extras', {}))
    data_dict.pop('__extras', None)

    if permission_labels:
        result = queriers[entity_name](data_dict, permission_labels)
    else:
        result = queriers[entity_name](data_dict)

    validated_results = []
    for doc in result["results"]:
        validated_results.append(json.loads(doc["validated_data_dict"]))

    return {
        "count": result["count"],
        "results": validated_results,
    }


def _get_user_page_labels(user_obj):

    labels = ["public"]

    if not user_obj:
        return labels

    if user_obj.sysadmin:
        labels.append("sysadmin")

    orgs = toolkit.get_action("organization_list_for_user")(
        {"user": user_obj.id}, {"permission": "admin"}
    )
    labels.extend("group_id-%s" % o["id"] for o in orgs)

    return labels
