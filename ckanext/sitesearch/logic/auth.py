def organization_search(context, data_dict):
    """All users can search organizations"""
    return {"success": True}


def group_search(context, data_dict):
    """All users can search groups"""
    return {"success": True}


def user_search(context, data_dict):
    """Only sysadmins can search users"""
    return {"success": False}
