
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

All `*_search` actions support most of the same paramters that [`package_search`](http://docs.ckan.org/en/latest/api/index.html#ckan.logic.action.get.package_search), except the `facet*` and `include_*` ones. That includes `q`, `fq`, `rows`, `start` and `sort`.


In all actions, the output matches the one of `package_search` as well, an object with a `count` key and a `results` one, wich is a list of the corresponding entities dict (ie the result of `organization_show`, `user_show` etc):

```
{
    "count": 2,
    "results": [
        <validated data dict 1>,
        <validated data dict 2>,
    ]
}

```

Additionally the plugin registers a `site_search` action that performs a search across all entities that the user is allowed to, including datasets. Results are returned in an object including the keys for which the user has permission to search on. For instance for a sysadmin user that has access to all searches:

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

Note that all parameters are passed unchanged to each of the search actions, so this site-wide search is mostly useful for free-text searches like `q=flood`.

### CLI

The plugin inlcudes a `ckan` command to reindex the current entities in the database in Solr:

    ckan sitesearch rebuild <entity_type>

Where `entity_type` is one of `organizations`, `groups`, `users` or `pages`. You can also pass the `id` or `name` of a particular entity to index just that particular one:

    ckan sitesearch rebuild organization department-of-transport


Check the command help for additional options:

    ckan sitesearch rebuild --help

### Logging search terms

The plugin includes a feature to log in the database all the search term for analytics purposes. For each search, it will log: term, entity_type, user_id (optional, default false) and timestamp.

`entity_type` can take the values of: `site`, `organization`, `group`, `dataset`, `pages`.


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

4. Run `ckan sitesearch initdb` to initialize the database

5. Restart CKAN

## Config settings

`ckanext.sitesearch.log_user_id`: Defaults to `False`. Set it to `True` if you want the ID of the user to be logged in the database. (We do not recommend this setting on public sites.)

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
