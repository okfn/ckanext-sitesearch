
# ckanext-sitesearch


[![Tests](https://github.com/okfn/ckanext-sitesearch/workflows/Tests/badge.svg?branch=main)](https://github.com/okfn/ckanext-sitesearch/actions)
[![Code Coverage](http://codecov.io/github/okfn/ckanext-sitesearch/coverage.svg?branch=main)](http://codecov.io/github/okfn/ckanext-sitesearch?branch=main)


Index different CKAN entities in Solr, not just datasets

## Requirements

This extension requires CKAN 2.9 or higher and Python 3

## Features


### Search actions

ckanext-sitesearch allows Solr-powered searches on the following CKAN entities:

| Entity | Action | Permissions | Notes |
| --- | --- | --- | --- |
| Organizations | `organization_search` | Public | |
| Groups        | `group_search`        | Public | |
| Users         | `user_search`         | Sysadmins only | |
| Pages         | `page_search`         | Public (individual page permissions apply) | Requires ckanext-pages |

All `*_search` actions support most of the same paramters that [`package_search`](http://docs.ckan.org/en/latest/api/index.html#ckan.logic.action.get.package_search), except the `include_*` ones. That includes `q`, `fq`, `rows`, `start`, `sort` and all the `facet*` ones.


In all actions, the output matches the one of `package_search` as well, an object with `count`, `results` and `search_facets` keys. `results` is a list of the corresponding entities dict (ie the result of `organization_show`, `user_show` etc):

```
{
    "count": 2,
    "results": [
        <validated data dict 1>,
        <validated data dict 2>,
    ],
    "search_facets": {
        <facet_field_1>: {
            "items": {
                "count": 1,
                "display_name": "example",
                "name": "example"
            },
            "title: "example"
        }
    }
}

```

### Site search

Additionally, the plugin registers a `site_search` action that performs a search across all entities that the user is allowed to, including datasets. Results are returned in an object including the keys for which the user has permission to search on. For instance for a sysadmin user that has access to all searches:

```
{
    "datasets": <results>,
    "organizations": <results>,
    "groups": <results>,
    "users": <results>,
    "pages": <results>
}
```

For each item, the results object is the one described above (`count` and `results` keys).

This action supports namespaced parameters to allow to pass certain search parameters to specific searches. To do, namespace the search param with the key of the relevant search, eg `datasets.limit=20`, `organizations.sort=title desc`, etc. Any non-namespaced parameters will be passed to all searches.

For instance consider the following input parameters for `site_search`:

```
data_dict = {
    "datasets.start": 0,
    "datasets.rows": 20,
    "datasets.facet.field": ["tags", "groups"],
    "groups.facet.field": ["type"],
    "q": "test",
    "fq": "state:active",
}
```

These will be parsed as following, and passed to the relevant search action:

```
search_params = {
    "datasets": {
        "start": 0,
        "rows": 20,
        "facet.field": ["tags", "groups"],
        "q": "test",
        "fq": "state:active",
    },
    "groups": {
        "facet.field": ["type"],
        "q": "test",
        "fq": "state:active",
    },
    "organizations": {
        "q": "test",
        "fq": "state:active",

    },
    "users": {
        "q": "test",
        "fq": "state:active",
    },
}
```



### CLI

The plugin inlcudes a `ckan` command to reindex the current entities in the database in Solr:

    ckan sitesearch rebuild <entity_type>

Where `entity_type` is one of `organizations`, `groups`, `users` or `pages`. You can also pass the `id` or `name` of a particular entity to index just that particular one:

    ckan sitesearch rebuild organization department-of-transport


Check the command help for additional options:

    ckan sitesearch rebuild --help


## Installation

To install ckanext-sitesearch:

1. Activate your CKAN virtual environment, for example:

     . /usr/lib/ckan/default/bin/activate

2. Clone the source and install it on the virtualenv

    git clone https://github.com/okfn/ckanext-sitesearch.git
    cd ckanext-sitesearch
    pip install -e .
	pip install -r requirements.txt

3. Add `sitesearch` to the `ckan.plugins` setting in your CKAN
   config file (by default the config file is located at
   `/etc/ckan/default/ckan.ini`).

4. Restart CKAN

## Config settings

None at present

## Developer installation

To install ckanext-sitesearch for development, activate your CKAN virtualenv and
do:

    git clone https://github.com/okfn/ckanext-sitesearch.git
    cd ckanext-sitesearch
    pip install -r dev-requirements.txt
    python setup.py develop


## Tests

To run the tests, do:

    pytest --ckan-ini=test.ini

## License

[AGPL](https://www.gnu.org/licenses/agpl-3.0.en.html)
