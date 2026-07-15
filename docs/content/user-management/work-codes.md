## Work Codes Management Guide

### Purpose

This guide explains how to manage work codes in User Management, including:

- Work code relationships
- Creating work codes
- Assigning work codes to user groups
- Unassigning work codes
- How work codes are used in the mobile app

### What is a Work Code?

A work code is a unique code that allows mobile app users to join an organisation's workspace.

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
- Assigning a work code to a user group gives all users in that group access to the associated organisation.
- Removing a work code from a user group removes the group's access to that organisation. The user group and work code are not deleted.

For more information about user groups, see [user groups](../user-groups) document.

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

The selected user groups can now use the work code to access the organisation.

#### Unassign a Work Code from a User Group

1. Go to **User Management**.
2. Select an organisation.
3. In the **Work Codes** section, select the work code.
4. Click **Actions** > **Unassign**.
5. Click **Save Changes** to confirm.

The selected user groups will no longer have access to the organisation through that work code.

### Work Codes in the Mobile App

Work codes allow mobile app users to join an organisation's workspace.

Users can:

- Enter a work code manually.
- Scan the QR code generated for the work code.

After entering or scanning a valid work code, users can access the organisation.

### Related Docs

- [Entity Relationships](../entity-relationships)
- [QA Guide](../qa-guide)
- [QR Codes](../qr-codes)