def is_super_user(user):
    return not user.is_anonymous and user.is_superuser


def is_in_group(user, group_name):
    return not user.is_anonymous and user.groups.filter(name=group_name).exists()


def is_org_admin(user):
    return is_in_group(user, "org_admin")


def is_58_admin(user):
    return is_in_group(user, "58_admin")


def is_super_or_58_admin(user):
    return is_super_user(user) or is_58_admin(user)
