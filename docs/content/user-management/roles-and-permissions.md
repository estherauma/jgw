## Roles And Permissions

### Purpose

This page explains how roles and permissions work inside User Management.

It covers:

- dashboard groups used when adding an admin user
- organisation roles used when adding a user inside an organisation
- default and custom organisation roles

### Roles And Permissions Overview

| Group | Name | Access scope | Access type | Notes |
|------|------|------|------|------|
| `58_admin` | Fifty Eight Administrator | All organisations | Dashboard | Broadest non-superuser access. Can manage global organisation setup. |
| `org_group_admin` | Organisation Group Administrator | Assigned organisation group | Dashboard | Access is limited to the organisation group assigned to the user. |
| `org_admin` | Organisation Administrator | Assigned organisation | Dashboard | Full organisation-level admin access for the assigned organisation. |
| `org_staff` | Organisation Staff | Assigned organisation | Dashboard | Used for organisation users with dashboard access but without full `org_admin` access. |
| `worker` | Worker | Assigned organisation | App | Mobile app access only. No dashboard access. |


### Organisation Roles

Each organisation starts with two default system roles:

- `Administrator`. This is the default organisation administrator role. It is used to create users with full dashboard access for the organisation. It is assigned to the `org_admin` group.
- `Worker`. This is the default organisation worker role. It is used to create users with app access only. It is assigned to the `worker` group.

Admins can also create additional custom organisation roles.

**Custom organisation roles:**

- belong to one organisation
- have permission flags assigned to them
- are used to define organisation-specific access
- when assigned to a user in the Add User flow, the user is added to the `org_staff` group
- the user can only access the actions allowed by the flags assigned to that role

### Related Docs

- [User Management Overview](../overview/)
- [Organisation Workflow](../organisation-workflow/)
- [QR Codes](../qr-codes/)
- [QA Guide](../qa-guide/)
