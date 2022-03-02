from ckan.plugins.interfaces import Interface


class ISiteSearch(Interface):
    """
    Hooks into the search actions to implement custom logic.

    These methods will be called before/after the search is performed to allow
    users to modify the search parameters or the search results.

    For the case of before_* methods, extensions will receive a dictionary with
    the query parameters, and should return a modified (or not) version of it.

    For the case of after_* methods (except site_search), extensions will
    receive the search results, as well as the search parameters, and should
    return a modified (or not) object with the same structure::

        {'count': '', 'results': '', 'search_facets': ''}

    Note that count and facets may need to be adjusted if the extension
    changed the results for some reason.
    """

    def before_site_search(self, search_params):
        """
        Called before the site search is performed.
        """
        return search_params

    def after_site_search(self, search_results, search_params):
        """
        Called after the site search is performed.

        This method has a specific search_results structure since it
        joins into one dictionary the results of the other searches. The
        expected structure is::
            {
                'datasets': {'count': '', 'results': '', 'search_facets': ''},
                'organizations': {'count': '', 'results': '', 'search_facets': ''},
                'groups': {'count': '', 'results': '', 'search_facets': ''},
                'users': {'count': '', 'results': '', 'search_facets': ''},
                'pages': {'count': '', 'results': '', 'search_facets': ''}
            }
        """
        return search_results

    def before_organization_search(self, search_params):
        """
        Called before the organization search is performed.
        """
        return search_params

    def after_organization_search(self, search_results, search_params):
        """
        Called after the organization search is performed.
        """
        return search_results

    def before_group_search(self, search_params):
        """
        Called before the group search is performed.
        """
        return search_params

    def after_group_search(self, search_results, search_params):
        """
        Called after the group search is performed.
        """
        return search_results

    def before_user_search(self, search_params):
        """
        Called before the user search is performed.
        """
        return search_params

    def after_user_search(self, search_results, search_params):
        """
        Called after the user search is performed.
        """
        return search_results

    def before_page_search(self, search_params):
        """
        Called before the page search is performed.
        """
        return search_params

    def after_page_search(self, search_results, search_params):
        """
        Called after the page search is performed.
        """
        return search_results
