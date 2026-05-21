from .utils import is_58_admin, is_org_admin, is_org_admin_or_staff, is_org_group_admin, is_org_or_group_admin, is_org_staff, is_super_user


def user_role(request):
    user = request.user
    return {
        "is_org_admin": is_org_admin(user),
        "is_org_group_admin": is_org_group_admin(user),
        "is_org_or_group_admin": is_org_or_group_admin(user),
        "is_58_admin": is_58_admin(user),
        "is_super_user": is_super_user(user),
        "is_org_staff":  is_org_staff(user),
        "is_org_admin_or_staff": is_org_admin_or_staff(user),
    }
