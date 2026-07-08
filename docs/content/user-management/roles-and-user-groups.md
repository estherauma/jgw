### Roles And User Groups

#### Purpose

This page explains how to create and manage organisation roles, assign permissions, create work groups, assign users to work groups, and how these settings affect user access.

#### Roles
A role defines what actions a user is allowed to perform within an organisation. Each role is associated with one or more permissions.

**Creating a Role**

To create a ne role;

1. Navigate to User Management
2. Select an organisation
3. Go to the **Roles** section
4. Click **Add role** button to open **Add role** form
5. In the add role form, fill in the **Name**, **Description** and select one or more permissions before saving.
6. Save the form

The newly added role will show in the roles table

**Validations**

- A role name is required
- Role names must be unique within an organisation
- Selecting permission is required

**Editing a role**

Only **custom roles** can be editing, system roles(Administrator and Worker) can not be edited.

To edit a role:

1. Navigate to User Management
2. Select an organisation
3. Go to the **Roles** section
4. Select a role and click **Edit** button
5. Update role details(name,description or permission)
6. Click **Save changes** button

Changes take effect immediately for users assigned to the role.

**Deleting a Role**

-Only **custom roles** can be deleted
-Roles with assigned users can not be deleted

**Permissions Mapping**
Permissions determine which features and actions are available to users assigned to a role.
When creating or editing a role, permissions are displayed as a checklist.

Examples of permissions include:

- Activate users
- Add organization groups
- Assign role permissions
- Assign users to departments

A role can have multiple permissions, and a permission can belong to multiple roles.

**Work Group (User Group)**

- A work group is used to organise users within an organisation.
- Each organisation can have multiple work groups.
- Work group names must be unique within the organisation.
- A work group belongs to only one organisation.

**Creating a Work Group**

1. Navigate to **User Management**
2. Select an organisation
3. Go to **User Groups** section
4. Click  **Create user group** button to open **Add User Group** form
5. Fill in the user group name in the form.
6. Click **Save**
7. Newly added user group will show in the table for user groups

**Editing a Work Group**

To edit a work group:

1. Navigate to **User Management**
2. Select an organisation
3. Go to **User Groups** section
4. Select a user group and click **Edit** button to open **Edit User Group** form
5. Update and click **Save changes** button

**Assign Users to Work Group**

1. Navigate to **User Management**
2. Select an organisation
3. Go to **Users** section
4. Select user(s)
5. Click **Actions** button to open the action menu
6. Select **Add to department** from the actions menu to open **Add users to user groups** form.
7. In the form,select department(s)
8. Click **Add** button

**Validation**

- The current user must have a permission to assign users to user groups.

**How Roles and Work Groups affect Access**

Roles and work groups serve different purposes.

**Roles**

Roles determine **what a user is allowed to do**

A role contains a collection of permissions that control access to features and actions.

For example, a role may allow a user to:

- Create users
- Create work codes
- Delete users

Changing the permissions assigned to a role immediately affects every user with that role.

**Work Groups**

- Work groups are used to organise users within an organisation.
- A user may belong to multiple work groups.
- Work groups themselves do not grant application permissions. Instead, they are used for grouping users and may be associated with organisation access codes where applicable.

