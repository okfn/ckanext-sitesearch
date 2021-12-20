import json

from ckan.plugins import toolkit


from ckanext.sitesearch.logic.schema import default_search_schema
from ckanext.sitesearch.lib import query


queriers = {
    "organization": query.query_organizations,
    "group": query.query_groups,
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

    result = queriers[entity_name](data_dict)

    validated_results = []
    for doc in result["results"]:
        validated_results.append(json.loads(doc["validated_data_dict"]))

    return {
        "count": result["count"],
        "results": validated_results,
    }
