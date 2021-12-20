
# ckanext-sitesearch

Index different CKAN entities in Solr, not just datasets

## Requirements

This extension requires CKAN 2.9 or higher

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
    python setup.py develop


## Tests

To run the tests, do:

    pytest --ckan-ini=test.ini

## License

[AGPL](https://www.gnu.org/licenses/agpl-3.0.en.html)
