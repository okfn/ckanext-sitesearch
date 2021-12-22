def organization_search(context, data_dict):
    """All users can search organizations"""
    return {"success": True}


def group_search(context, data_dict):
    """All users can search groups"""
    return {"success": True}


def user_search(context, data_dict):
    """Only sysadmins can search users"""
    return {"success": False}


def page_search(context, data_dict):
    """All users can search pages

    Note that as in datasets, permission labels apply to limit the results returned
    """
    return {"success": True}


def site_search(context, data_dict):
    """All users can search across all entities

    Note that for each individual entity an additonal auth check will be done, eg
    if the user is not allowed to search users, they won't get any users results
    """
    return {"success": True}
