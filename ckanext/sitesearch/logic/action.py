import json

from ckan.plugins import toolkit


from ckanext.sitesearch.logic.schema import default_search_schema
from ckanext.sitesearch.lib.query import query_organizations


@toolkit.side_effect_free
def organization_search(context, data_dict):

    toolkit.check_access("organization_search", context, data_dict)

    schema = context.get("schema") or default_search_schema()

    data_dict, errors = toolkit.navl_validate(data_dict, schema, context)
    if errors:
        raise toolkit.ValidationError(errors)

    if not data_dict.get("sort"):
        data_dict["sort"] = "title asc"

    result = query_organizations(data_dict)

    validated_results = []
    for doc in result["results"]:
        validated_results.append(json.loads(doc["validated_data_dict"]))

    return {
        "count": result["count"],
        "results": validated_results,
    }
