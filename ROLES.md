Roles & Permissions (User Management)
=====================================

Overview
--------
User Management uses two layers:
- Organisation roles (stored in `OrganisationRole`) control feature access via feature flags.
- Django groups (e.g., `org_admin`, `org_staff`) identify broad access categories and gate some flows.

Organisation Roles
------------------
There are system roles and custom roles:
- System roles: `Administrator`, `Worker`
- Custom roles: any non-system role created per organisation

When a role is saved:
- All roles grant dashboard access except `Worker`.
- `Worker` is the only role that does not grant dashboard access.

Role Assignments
----------------
Each user can have one role per organisation via `OrganisationRoleAssignment`.
This assignment is used to evaluate permissions for that organisation.

When a role is applied to a user (`apply_role_to_user`):
- Dashboard roles set `user.access_type = "dashboard"` and `user.is_active = True`.
- `org_admin` and `org_staff` are mutually exclusive for dashboard users:
  - System role -> add `org_admin`, remove `org_staff`.
  - Custom role -> add `org_staff`, remove `org_admin`.
- App roles set `user.access_type = "app"` and remove `org_admin`, `org_staff`, and `user_management`.

Django Groups
-------------
- `org_admin`: system dashboard role access.
- `org_staff`: custom role dashboard access.
- `user_management`: required to access the user management page.
- `58_admin`: global admin access across all organisations.

`org_staff` is not selectable in the UI. It is assigned automatically when a user is given a custom role.

Feature Flags
-------------
Permissions are defined in `user_management/flags.py` (`UM_FLAG_DEFS`).
These flags are stored as `waffle.Flag` rows and used as permissions.

Flag checks happen through `is_flag_active`:
- If the user is in `org_admin` or `58_admin`, waffle rules (`flag.is_active(request)`) are used.
- Otherwise, the user must have the flag via their organisation role permissions.

Server-side Enforcement
-----------------------
All user management views enforce permissions server-side by calling:

`has_org_access(user, organisation, request, flag_name)`

For org_admin/org_staff, this ensures both:
- the user has access to the organisation, and
- the required flag is active for that organisation.

`58_admin` users are not restricted to a single organisation and are allowed across all orgs.

Deleting Roles
--------------
Roles cannot be deleted if they have assigned users. Users must be unassigned first.

Default Roles
-------------
Default roles are created when an organisation is created via:
- `add_default_org_roles(organisation)`

The management command `assign_default_org_roles` also backfills defaults for existing orgs.
