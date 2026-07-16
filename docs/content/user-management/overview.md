## User Management Overview
### Purpose

The User Management module is used to manage how users access content in the Just Good Work mobile application.

It supports both internal platform administrators and organisation-based administrators in setting up and controlling access for the organisations they manage.

Through User Management, authorised users can manage:

- Organisations
- Work codes
- User groups
- Roles and permissions
- Users
- Organisation deep links

It is primarily used by:

- superusers
- `58_admin` users, who are Fifty Eight administrators
- organisation admins
- organisation group admins
- organisation staff, depending on the action and permission flag

### Main Goals

User Management exists to support the setup and ongoing management of access for each organisation in the Just Good Work mobile application.

It is where authorised users can:

- Create and update organisation records
- Select an organisation and work within its scope
- Manage work codes and login QR code flows
- Manage user groups and role permissions
- Manage app users and dashboard users
- Create and edit organisation onboarding deep links

### How The Page Works

The User Management page is organisation-scoped for most actions.

That means a user usually:

1. Selects an organisation
2. Sees data and actions related to that organisation
3. Performs create, edit, assign, or deep-link actions inside that context

Some sections are global for higher-permission users, while others depend directly on the currently selected organisation.

### Main Page Sections

#### Organisations

This section is the starting point for most setup work.

It is used to:

- Create organisations
- Edit organisation details
- Search organisations

Organisation records are the parent entity for several other User Management tables.

Important implementation detail:

- When an organisation is created, it is synced to the Strapi CMS partner configuration data.

For the full organisation page flow, see [Organisation Workflow](../organisation-workflow/).

#### Organisation Groups

Organisation groups are used to manage collections of organisations together.

This section is used to:

- Create organisation groups
- Edit organisation groups
- Attach organisations to a group
- Remove organisations from a group

Organisation groups are especially important where administration happens across multiple organisations instead of only one.

For the data relationships behind organisation grouping, see [Entity Relationships](../entity-relationships/).

#### Selected Organisation

The selected organisation drives the context for downstream sections.

When an organisation is selected, the page uses that organisation to:

- Load work codes
- Load organisation roles
- Load deep links
- Load other organisation-specific actions and details

#### Work Codes

Work codes belong to an organisation and are used in login and access flows in the Just Good Work mobile application.

This section supports:

- Creating work codes
- Assigning and unassigning work codes to user groups
- Generating login deep links and QR codes

Important access rule:

- A work code can be assigned to many user groups.
- If a work code is not assigned to any user group, it can be accessed by all users in that organisation.
- If a work code does not require authentication, anyone who has access to the code can use it.

#### User Groups

User groups are used to organise users and control access to content through work codes.
In practice, a user group may represent a department or another organisational grouping.

They are used to:

- Group users
- Support work code assignment
- Control which content users can access through the work codes assigned to that group

Important access rules:

- A user can belong to more than one user group.
- A user can only access content available through the user group or groups they belong to.

#### Roles and Role Permissions

Roles define the permissions available within an organisation.

This section supports:

- Creating roles
- Editing roles
- Deleting roles
- Assigning permission flags to each role

These permissions are then used by the application to determine which actions a user can perform.

For the full roles and permissions model, see [Roles and Permissions](../roles-and-permissions/).

#### Organisation Deep Links

Organisation deep links are onboarding links created for an organisation.

[Branch](https://branch.io/) is used to generate, store, and update the deep-link data for these links.

This section supports:

- Creating onboarding deep links
- Editing existing deep links
- Viewing a QR code for a saved deep link

For more details about QR-code creation and storage, see [QR Codes](../qr-codes/).


#### Users

User-related actions in User Management cover both app users and dashboard users, depending on the workflow.

These actions include:

- Creating users
- Editing users
- Activating, deactivating, or inviting users
- Assigning users to work groups

#### Permissions

Access inside User Management is not the same for all users.

At a high level:

- Superusers and `58_admin` users have the broadest visibility
- Organisation admins and organisation staff are restricted to the organisations they can access
- Certain actions are protected by specific permission flags

For the detailed permission model, see [Roles and Permissions](../roles-and-permissions/).

### Related Docs

- [Organisation Workflow](../organisation-workflow/)
- [Roles and Permissions](../roles-and-permissions/)
- [Entity Relationships](../entity-relationships/)
- [QR Codes](../qr-codes/)
- [QA Guide](../qa-guide/)
- [Work Codes](../work-codes)
