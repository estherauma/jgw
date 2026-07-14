## Work Codes Management Guide

### Purpose
This page explains how to manage Work Codes within User Management, covering;

- Creation of work code, 
- Assignment of work code, 
- Un assignment of work code, 
- Login QR code/deep link generation, 
- Relationships.


### 1. Managing Work Codes

#### Create a Work Code
1. Navigate to **User Management** and select an organization. 
    - *Note: Organization administrators are permanently attached to a single organization and do not need to select one*.
2. Under the **Work Codes** section, click **Create work code**.
3. Fill in the **Work code** and optional **Expiry date** fields.
4. Click **Save**. The new code will appear in the work codes table.

#### Assign a Work Code to a User Group
1. Navigate to **User Management** and select an organization.
2. Under the **Work Codes** section, select the target work code.
3. Click **Actions** and select **Assign** to open the assignment form.
4. Select the target user groups and click **Assign**.

#### Unassign a Work Code
1. Navigate to **User Management** and select an organization.
2. Under the **Work Codes** section, select the target work code.
3. Click **Actions** and select **Unassign**.
4. Click **Save changes** on the confirmation modal.


### 2. QR Codes and Deep Links

#### Generate a Login QR Code
It's used to authenticate and log into the mobile application:

1. Under the **Work Codes** section of of the selected organization, locate the target work code and click **Actions**.
2. Select **QR code**. From here, you can scan the code, copy the login link, or download the QR code.

#### Generate an Onboarding QR Code (Deep Links)
It's used to route users to specific onboarding flows:

1. Go to the **Organisation QR Codes** section.
2. Click **Create link**.
3. Fill in the required fields and click **Save**.
    * *Note: You can edit, download, or delete existing links directly from the actions menu in the table.*


### 3. Relationships

#### Organisation to Work Codes

**Relationship:** Each work code belongs to a single organisation.

**What it means:**

- A work code can only exist within one organisation.
- Work codes cannot be shared or used across different organisations.
- An organisation can have multiple work codes.

#### User Groups to Work Codes

**Relationship:** User groups and work codes have a many-to-many relationship.

**What it means:**

- A user group can be assigned multiple work codes.
- A work code can be assigned to multiple user groups.
- Assigning a work code to a user group grants all users in that group access to the associated organisation.
- Removing a work code from a user group removes that organisation access for all users in the group. The user group and work code remain unchanged.