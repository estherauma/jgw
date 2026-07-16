## Work Codes Management Guide

### Purpose

This guide explains how to manage work codes in User Management, including:

- Work code relationships
- Creating work codes
- Assigning work codes to user groups
- Unassigning work codes
- How work codes are used in the mobile app

### What is a Work Code?

A work code is a unique code that controls which organisation content a user can access in the mobile app.

### Who Can Create Work Codes?

- Superusers
- Fifty Eight administrators
- Organisation administrators
- Organisation group administrators
- Organisation staff with the permission to create work codes

### Work Code Relationships

#### Organisations

- A work code belongs to only one organisation.
- An organisation can have multiple work codes.

For more information about organisations, see [organisation workflow](../organisation-workflow) document.

#### User Groups

User groups and work codes have a many-to-many relationship.

- A user group can be assigned multiple work codes.
- A work code can be assigned to multiple user groups.
- Assigning a work code to a user group gives all users in that group the ability to see content for the organisation linked to that work code.
- If a work code is not assigned to any user group, then all users in that organisation can see the content linked to that work code.

For more information about user groups, see [user groups](../user-groups) document.

### Work Codes in the Mobile App

- Work codes allow mobile app users to get access to the organisation content linked to work codes.
- Users scan the QR code generated for a work code.
- After scanning the QR code, users can access the organisation content linked to the work code.

### Managing Work Codes

#### Create a Work Code

1. Go to **User Management**.
2. Select an organisation.
   - **Note:** Organisation administrators are permanently assigned to a single organisation and do not need to select one.
3. In the **Work Codes** section, click **Create Work Code**.
4. Enter the **Work Code**.
5. (Optional) Select an **Expiry Date**.
6. Click **Save**.

The new work code appears in the **Work Codes** table.

#### Assign a Work Code to a User Group

1. Go to **User Management**.
2. Select an organisation.
3. In the **Work Codes** section, select the work code.
4. Click **Actions** > **Assign**.
5. Select one or more user groups.
6. Click **Assign**.

The selected user groups can now use the work code to access the organisation data linked to the work code.

#### Unassign a Work Code from a User Group

1. Go to **User Management**.
2. Select an organisation.
3. In the **Work Codes** section, select the work code.
4. Click **Actions** > **Unassign**.
5. Click **Save Changes** to confirm.

All users in the organisation will then be able to see data for the organisation linked to that work code.

### Related Docs

- [Entity Relationships](../entity-relationships)
- [QA Guide](../qa-guide)
- [QR Codes](../qr-codes)