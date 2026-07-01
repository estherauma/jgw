### User management Data Model and Tables
#### Overview
A **model** and a **table** are related but not the same:

 - A **model** is the Django class for example, OrganisationData.
  - A **table** is the database table created from that model for example, organisation_data.

The User Management data model defines how organisations, users, roles, permissions, work groups and related information are stored in the database.

Each Django model is stored in a corresponding database table. These tables are connected through relationships that allow the system to manage organisations, assign users and roles, organize work groups, record user activity, and store supporting information.

The following sections describe the purpose of each model, its key fields, and its relationships with other models.

#### 1. OrganizationGroup
**Database Table:** `organisation_group`

The `OrganizationGroup` model represents a group of organizations. It is used to organize multiple organisations under a single group for easy management.

**Key fields**

   - Name
   - Group Code
   - CMS ID
   - CMS Sync Status
   - Custom Type

**Relationships**

- One organisation group can contain many organisations.

#### 2. OrganisationData
**Database Table:** `organisation_data`

The `OrganisationData` model represents an organisation. It is the central model in the User Management module and stores the organization's configuration.

**Key fields**

   - Name
   - Organisation Code
   - Display Name
   - Organization Group
   - Theme
   - Work Sector
   - Content Collection
   - Default Collection Language
   - Default Report Issue Emails
   - Default Feedback Emails
   - Big Icon
   - Small Icon
   - CMS ID
   - CMS Sync Status

**Relationships**

An organisation:

- belongs to one organisation group
- has many work groups
- has many roles
- has many role assignments
- has many deep links
- has many activity logs
- has many access codes

#### 3. OrganisationAccessCode
**Database Table:** `organisation_access_code`

The `OrganisationAccessCode` model stores access codes for an organization. These access codes allow workers to join the correct organization.

**Key fields**

   - Access Code
   - Organisation

**Relationships**

Organisation access code:

- belongs to one organisation.
- can be assigned to multiple work groups.

#### 4. WorkGroup
**Database Table:** `work_group`

The `WorkGroup model` represents a team or department within an organization.

**Key fields**

   - Name
   - Organisation

**Relationships**

A work group:

- belongs to one organisation.
- can have multiple access codes.
- has a many-to-many relationship with organisation access codes.

#### 5. OrganisationRole
**Database Table:** `organisation_role`

The `OrganisationRole` model defines a role within an organization. Roles determine the permissions available to users.

**Key fields**

   - Name
   - Description
   - Grants Dashboard Access
   - System Role

**Relationships**

An organisation role:

- belongs to one organisation.
- has many role permissions.
- has many role assignments.

#### 6. OrganisationRolePermission
**Database Table:** `organisation_role_permission`

The `OrganisationRolePermission` model links an organisation role to a feature flag. It defines the permissions assigned to a role.

**Key fields**

   - Role
   - Feature Flag

**Relationships**

An organisation role permission:

- belongs to one organization role.
- belongs to one feature flag.

#### 7. OrganisationRoleAssignment
**Database Table:** `organisation_role_assignment`

The `OrganisationRoleAssignment` model assigns an organization role to a user within a specific organization.

**Key fields**

   - User
   - Organisation
   - Role

**Relationships**

Organisation role assignment:

- belongs to one user.
- belongs to one organization.
- belongs to one role.

#### 8. OrganisationDeepLink
**Database Table:** `organisation_deep_link`

The `OrganisationDeepLink` model stores deep links for an organization.

These links allow users to open specific pages or features directly from the mobile application.

**Key fields**

   - Organisation
   - Link
   - Link Type
   - Title

**Relationships**

Organisation deep link:

- belongs to one organisation.

#### 9. UserActivity
**Database Table:** `user_activity`

The `UserActivity model` records important actions performed in the User Management module.

These records provide an audit trail and cannot be modified or deleted after they are created.

**Key fields**

   - Actor
   - Action
   - Record Type
   - Record ID
   - Organisation
   - Message
   - Changes
   - Created At

**Relationships**

User activity:

- belongs to one organisation.
- belong to one user (actor).

#### 10. ShortLink
**Database Table:** `short_link`

The `ShortLink` model stores shortened URLs. It generates a unique code that redirects users to a longer target URL. Short links can optionally expire after a specified date and time.

**Key fields**

   - Code
   - Target URL
   - Expires At
   - Created At

**Relationships**

- This model does not have relationships with other User Management models.