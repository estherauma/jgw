## Roles and User Groups

### Purpose
This document provides a guide on managing roles, permissions, and user groups within an organisation, explaining their workflows and how they control user access in User Management.

### 1. Roles and Permissions Mapping

#### What is a Role?
A role defines what actions a user is authorized to perform within an organisation. Each role is associated with a specific set of permissions.

There are two categories of roles:

* **System Roles:** Pre-defined roles (e.g., `Administrator` and `Worker`) that cannot be edited or deleted.
* **Custom Roles:** User-defined roles tailored to specific organisational needs that can be edited or deleted.

#### What are Permissions?
Permissions determine the exact features and actions available to a role. They are mapped as a many-to-many relationship: a role can have multiple permissions, and a permission can be mapped to multiple roles.

**Examples of Permissions:**

* Activate users
* Add organization groups
* Assign role permissions
* Assign users to departments

#### Workflow: Create a Custom Role
1. Navigate to **User Management** and select the target organisation.
2. Go to the **Roles** section.
3. Click the **Add role** button to open the form.
4. Fill in the **Name** and **Description**.
5. Select one or more permissions from the checklist.
6. Click **Save**. The new role will appear in the roles table.

##### Validations:
* Role name is required.
* Role names must be unique within the organisation.
* At least one permission must be selected.

#### Workflow: Edit a Custom Role
1. Navigate to **User Management** and select the target organisation.
2. Go to the **Roles** section.
3. Locate the custom role and click the **Edit** button.
4. Update the role details (Name, Description, or Permissions).
5. Click **Save changes**. 
    * *Note: Changes take effect immediately for all users assigned to this role.*

#### Workflow: Delete a Custom Role
* Only **custom roles** can be deleted.
* A role cannot be deleted if it currently has users assigned to it.

### 2. User Groups

#### What is a User Group?
A User Group is a functional or departmental unit used to organize users within an organisation.

* An organisation can have multiple user groups.
* A user group belongs exclusively to one organisation.
* User group names must be unique within the organisation.

#### Workflow: Create a User Group
1. Navigate to **User Management** and select the target organisation.
2. Go to the **User Groups** section.
3. Click the **Create user group** button to open the form.
4. Enter the user group name.
5. Click **Save**. The group will appear in the user groups table.

#### Workflow: Edit a User Group
1. Navigate to **User Management** and select the target organisation.
2. Go to the **User Groups** section.
3. Locate the target user group and click the **Edit** button.
4. Update the name and click **Save changes**.

### 3. User Assignment Workflow

#### Assigning Users to a User Group
1. Navigate to **User Management** and select the target organisation.
2. Go to the **Users** section.
3. Select one or multiple user(s) using the checkboxes.
4. Click the **Actions** button to open the action menu.
5. Select **Add to department** to open the **Add users to user group** form.
6. Select the target user group(s) from the list.
7. Click the **Add** button.

##### Validations:
* The performing user must have the **Assign users to departments** permission to assign users to user groups.

### 4. System Logic: How Roles vs. Groups Affect Access

Roles and User Groups serve distinct architectural purposes:

| Feature | Primary Purpose | Impact on Access / Permissions | Scalability |
| :--- | :--- | :--- | :--- |
| **Roles** | Dictates **what** actions a user can do. | **Directly grants functional privileges.** Controls access to specific system features. | Changes to a role immediately update permissions for all assigned users. |
| **User Groups** | Dictates **who** belongs together structurally. | **Does not grant application permissions.** Used strictly for logical grouping, organisational structure, or mapping to organisation access/work codes. | A user can belong to multiple groups simultaneously without affecting their functional capabilities. |