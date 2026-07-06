### User management Data Model and Tables
#### Overview
A **model** and a **table** are related but not the same:

   - A **model** is the Django class for example, OrganisationData.
   - A **table** is the database table created from that model for example, organisation_data.

The User Management data model defines how organisations, users, roles, permissions, work groups and related information are stored in the database.

Each model is stored in a corresponding database table. These tables are connected through relationships that allow the system to manage organisations, assign users and roles, organize work groups, record user activity, and store supporting information.

The following sections describe the purpose of each model, and its relationships with other models.

#### 1. OrganizationGroup (Organisation Group)
**Database Table:** `preference_organizationgroup`

The `OrganizationGroup` model represents a group of organisations. It is used to organize multiple organisations under a single group for easy management.

**Relationships**

- One organisation group can contain many organisations.

#### 2. OrganisationData (Organisations)
**Database Table:** `preference_organisationdata`

The `OrganisationData` model represents an organisation. It is the central model in the User Management module and stores the organisation's configuration.

**Relationships**

An organisation:

- may belong to one organisation group (optional).
- can have many work groups.
- can have many roles.
- can have many role assignments.
- can have many deep links.
- can have many activity logs.
- can have many access codes.

#### 3. OrganisationAccessCode (Work Code)
**Database Table:** `preference_organisationaccesscode`

The `OrganisationAccessCode` model stores access codes for an organisation. These access codes allow workers to join the correct organisation.

**Relationships**

Organisation access code:

- may belong to one organisation (optional).
- can be assigned to multiple work groups.

#### 4. WorkGroup (User Group)
**Database Table:** `user_management_workgroup`

The `WorkGroup model` represents a team or department within an organisation.

**Relationships**

A work group:

- belongs to one organisation.
- can have multiple access codes.
- can have many users.

#### 5. OrganisationRole (Role)
**Database Table:** `user_management_organisationrole`

The `OrganisationRole` model defines a role within an organisation. Roles determine the permissions available to users.

**Relationships**

An organisation role:

- has one organisation.
- has many role permissions.
- has many role assignments.

#### 6. OrganisationRolePermission (Permission)
**Database Table:** `user_management_organisationrolepermission`

The `OrganisationRolePermission` model links an organisation role to a feature flag. It defines the permissions assigned to a role.

**Relationships**

An organisation role permission:

- has one organisation role.
- has one feature flag.

#### 7. OrganisationRoleAssignment
**Database Table:** `user_management_organisationroleassignment`

The `OrganisationRoleAssignment` model assigns an organisation role to a user within a specific organisation.

**Relationships**

Organisation role assignment:

- has one user.
- has one organisation.
- has one role.

#### 8. OrganisationDeepLink (Organisation QR Code)
**Database Table:** `preference_organisationdeeplink`

The `OrganisationDeepLink` model stores deep links for an organisation.

These links allow users to open specific pages or features directly from the mobile application.

**Relationships**

Organisation deep link:

- has one organisation.

#### 9. UserActivity (User Activity Logs)
**Database Table:** `user_management_useractivity`

The `UserActivity model` records important actions performed in the User Management module.

These records provide an audit trail and cannot be modified or deleted after they are created.

**Relationships**

User activity:

- has one organisation.
- has one user (actor).

#### 10. User

The `User` model stores information about system users.

**Relationships**
A user:

 - can have many activity records.
 - can be assigned one or more roles within an organisation.
 - can only have one organisation.

#### 11. ShortLink
**Database Table:** `short_link`

The `ShortLink` model stores shortened URLs. It generates a unique code that redirects users to a longer target URL. Short links can optionally expire after a specified date and time.

**Relationships**

- This model does not have relationships with other User Management models.

#### User Management Entity Relationship Diagram (ERD)

<img src="/static/erd.png" alt="User Management ERD" width="800" />