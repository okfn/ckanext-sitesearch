import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit


from ckanext.sitesearch.cli import get_commands
import ckanext.sitesearch.logic.action as action
import ckanext.sitesearch.logic.auth as auth


class SitesearchPlugin(plugins.SingletonPlugin):

    plugins.implements(plugins.IActions)
    plugins.implements(plugins.IAuthFunctions)
    plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.IClick)

    # IConfigurer

    def update_config(self, config_):
        if not toolkit.check_ckan_version(min_version="2.9.0"):
            raise RuntimeError("This extension requires at least CKAN 2.9")

    # IActions

    def get_actions(self):
        return {
            "organization_search": action.organization_search,
            "group_search": action.group_search,
        }

    # IAuthFunctions

    def get_auth_functions(self):
        return {
            "organization_search": auth.organization_search,
            "group_search": auth.group_search,
        }

    # IClick

    def get_commands(self):

        return get_commands()
