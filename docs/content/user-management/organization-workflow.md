## Organisation Workflow

### Purpose

The Organisation workflow module manages organisations in the Just Good Work admin dashboard. It allows authorized users to create, update and manage organisations and their related information.

### Role-Based Access

The information and actions available in the Organisation module depend on the user's role.

| Role | Access |
|------|--------|
| **Superuser and Fifty Eight Admin** | Can view and manage data for all organisations. |
| **Organisation Group Admin** | Manages organisation group. |
| **Organisation Admin** | Manages the organisation they are assigned to. They do not see the list of organisations and cannot switch between organisations. |
| **Organisation Staff** | Can only view and manage the information they have permission to access within their organisation. |

### Process Flow

1. **Login:** The user logs in to the system. Access to the Organization module depends on the user's role (Superuser, Fifty Eight Admin, Organisation Admin, Organisation Group Admin, or Organisation Staff).

2. **Navigating to user management page:** The user selects **User Management** from the sidebar to open the Organisation module.

3. **The user management page:** The user management page displays the following sections:

    - Selected Organisation
    - Organisations
    - Organisation Groups
    - Users

4. **Manage Organisations:** Depending on their permissions, users can:

    - Create organisations.
    - Edit organizations.
    - Select an organization to manage its data.
    - Search organisations.

### Sections & Actions

#### 1. Selected Organisation

The selected organization determines the information displayed in the rest of the dashboard.

##### Organisation Selection Behavior

1. Click the **Select organisation** dropdown.
2. Select the organisation you want to manage.
3. The dashboard automatically updates to display information for the selected organisation, including:
    - Work Codes
    - Users
    - User Groups
    - Roles
    - Organisation QR Codes
    - Organisation Languages
    - Organisation Details

After selecting an organization, you can also:

 - Create a Work Code
 - Create a User Group
 - Add a User
 - Add a Role
 - Add organisation QR code

#### 2. Organisations

This section displays all organisations in the system.

##### Create Organisation

1. Click **Add Organisation** button.
2. Fill in all required fields.
3. Click **Save**.
4. The new organization is added to the Organisations table.

##### Edit Organisation

1. Click the **Edit** button for the organisation you want to update.
2. Update the allowed fields.
3. Click **Save changes**.

> **Note:**  
The **Name**, **Code**, **Access Code**, and **Custom type** fields are read-only during editing and cannot be changed.

##### Search and Pagination Behavior

- Use the search field above the Organisations table to search for an organisation.
- The Organisations table displays a maximum of **20 organisations per page**.
- Use the pagination controls at the bottom of the table to navigate between pages.

#### 3. Organisation Groups

This section is used to manage organisation groups.

1. Click **Add organisation group** button.
2. Enter the required information.
3. Click **Save**.
4. The new organisation group appears in the Organisation Groups table.

> **Note:**  
The Create new organisation group form contains only two required fields:

 - **Name**
 - **Code**

#### 4. Users

This section displays users based on the selected organisation and the current user's permissions.