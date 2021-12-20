from ckan.logic.schema import validator_args


@validator_args
def default_search_schema(
    ignore_missing,
    unicode_safe,
    list_of_strings,
    natural_number_validator,
    int_validator,
    convert_to_json_if_string,
    convert_to_list_if_string,
    limit_to_configured_maximum,
    default,
):
    return {
        "q": [ignore_missing, unicode_safe],
        "fl": [ignore_missing, convert_to_list_if_string],
        "fq": [ignore_missing, unicode_safe],
        "rows": [
            default(10),
            natural_number_validator,
            limit_to_configured_maximum("ckan.search.rows_max", 1000),
        ],
        "sort": [ignore_missing, unicode_safe],
        "start": [ignore_missing, natural_number_validator],
        "qf": [ignore_missing, unicode_safe],
        "facet": [ignore_missing, unicode_safe],
        "facet.mincount": [ignore_missing, natural_number_validator],
        "facet.limit": [ignore_missing, int_validator],
        "facet.field": [ignore_missing, convert_to_json_if_string, list_of_strings],
    }
