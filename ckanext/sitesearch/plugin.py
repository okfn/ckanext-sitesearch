import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit


from ckanext.sitesearch.cli import get_commands
import ckanext.sitesearch.logic.action as action
import ckanext.sitesearch.logic.chained_action as chained_action
import ckanext.sitesearch.logic.auth as auth


class SitesearchPlugin(plugins.SingletonPlugin):

    plugins.implements(plugins.IActions)
    plugins.implements(plugins.IAuthFunctions)
    plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.IClick)
    plugins.implements(plugins.IPackageController, inherit=True)

    # IConfigurer

    def update_config(self, config_):
        if not toolkit.check_ckan_version(min_version="2.9.0"):
            raise RuntimeError("This extension requires at least CKAN 2.9")

    # IActions

    def get_actions(self):
        actions = {
            "organization_search": action.organization_search,
            "group_search": action.group_search,
            "user_search": action.user_search,
            "site_search": action.site_search,
            "organization_create": chained_action.organization_create,
            "organization_update": chained_action.organization_update,
            "organization_delete": chained_action.organization_delete,
            "group_create": chained_action.group_create,
            "group_update": chained_action.group_update,
            "group_delete": chained_action.group_delete,
            "user_create": chained_action.user_create,
            "user_update": chained_action.user_update,
            "user_delete": chained_action.user_delete,
            "package_create": chained_action.package_create,
            "package_delete": chained_action.package_delete,
            "member_create": chained_action.member_create,
        }
        if plugins.plugin_loaded("pages"):
            actions["page_search"] = action.page_search
            actions["ckanext_pages_update"] = chained_action.pages_update
            actions["ckanext_pages_delete"] = chained_action.pages_delete

        return actions

    # IAuthFunctions

    def get_auth_functions(self):
        auth_functions = {
            "organization_search": auth.organization_search,
            "group_search": auth.group_search,
            "user_search": auth.user_search,
            "site_search": auth.site_search,
        }
        if plugins.plugin_loaded("pages"):
            auth_functions["page_search"] = auth.page_search

        return auth_functions

    # IClick

    def get_commands(self):

        return get_commands()

    # IPackageController

    def before_search(self, search_dict):
        return self._before_dataset_search(search_dict)

    def before_dataset_search(self, search_dict):
        return self._before_dataset_search(search_dict)

    def _before_dataset_search(self, search_dict):
        """Ensure we are only returning datasets"""

        if "fq_list" not in search_dict:
            search_dict["fq_list"] = []

        search_dict["fq_list"].append("+entity_type:package")

        return search_dict
