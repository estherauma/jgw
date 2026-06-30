## User Management QA Guide

### Purpose

This guide is for a QA tester who already has a `58_admin` account and needs to test the full User Management feature end to end.

The goal is to verify that User Management correctly supports:

- Organisation setup.
- Organisation group setup.
- User creation and assignment.
- Work code access rules.
- User group access rules.
- Roles and permission enforcement.
- Organisation deep links.
- Audit and regression behaviour.

### Start Here

QA should start with the existing `58_admin` account.

That account should be used to create the base test data for the rest of the guide.



### Step 1: Log In As `58_admin`

Confirm that the `58_admin` account can:

- Access User Management.
- See the selected organisation dropdown.
- See the organisations table.
- See the organisation groups table.
- See User Activity Logs.

Then select an organisation and confirm that QA can see the organisation-specific sections update to show data for that organisation, including:
- Organisation-specific users.
- Work codes.
- User groups.
- Roles and role permissions.
- Organisation deep links.
- Organisation details.

Also confirm that changing the selected organisation updates those organisation-scoped sections consistently.

### Step 2: Create An Organisation

Create a new organisation and use it as the main test organisation for the rest of the guide.

Access rule:

- Only a `58_admin` user can create or edit organisations.
- Only a `58_admin` user can edit organisation details.

Confirm that QA can:

- Open the create organisation modal.
- Submit valid organisation details.
- Save successfully.
- See the organisation in the organisations table.
- Search for the organisation.
- Open the edit flow and update the organisation.
- Open the `Organisation details` section and edit the organisation details as a `58_admin` user.

Also confirm that QA tests that an `org_admin` user cannot edit organisation details.

Also confirm:

- Validation errors display correctly for required fields.
- The created organisation is synced to the Strapi CMS partner configuration data. Go to [Test CMS](https://test.cms.50eight.com/) and confirm that the new organisation appears in the partner configuration collection.

### Step 3: Create An Organisation Group
Create an organisation group and attach the new organisation to it.

Access rule:

- Only a `58_admin` user can create or edit organisation groups.

Confirm that QA can:

- Create an organisation group.
- Edit the organisation group.
- Attach the organisation to the group.
- Remove the organisation from the group.

Also confirm the organisation group appears correctly in the organisation groups table.

### Step 4: Creating Users

Keep the credentials for each created user, because QA will need to sign in as those users later.

Tip:

- QA can use the same Fifty Eight email inbox for multiple test users by using `+` aliases. For example, `youremail+2@fiftyeight.io` is treated as a different email address by the platform, but the invitation will still be delivered to the same inbox.

General rule for every user created in this step:

- If `Send Invite` is checked, confirm that the user receives an email invitation and can use it to set up the account.
- Confirm that each created user can sign in with the credentials or setup flow provided.

#### Create An Organisation Admin

Also confirm this visibility rule:

- `Add Admin` should only be visible to `58_admin` users.

Confirm that QA can:

- Open the `Add Admin` flow without selecting an organisation first.
- Create a user with `user_management` and `org_admin` selected under role and permissions.


#### Create An Organisation Staff User

Access rule:

- An organisation admin can create an organisation staff user.
- An organisation group admin can create an organisation staff user.
- A `58_admin` user can also create an organisation staff user.

Confirm that QA can:

- Create a custom role first under the roles table for the selected organisation.
- Assign the required permission  to that role.
- Click `Add User` from users table.
- Select the custom role when creating the staff user.

#### Create An Organisation Group Admin

If organisation-group behaviour is being tested, confirm that QA can:

- Open the `Add Admin` flow without selecting an organisation first.
- Create a user with `user_management` and `org_group_admin` selected under role and permissions.

#### Create A Worker Or App User

Access rule:

- A `58_admin` user can create a worker or app user.
- An organisation admin can create a worker or app user.
- An organisation group admin can create a worker or app user.
- An organisation staff user can create a worker or app user only if they have permission to add a user.

Workers are the users who will use the Just Good Work application.

***Note that SMS invitations are currently not working, so QA should only test email invitations.***

Confirm that QA can:

- Select an organisation first.
- Go to the users table and click `Add User`.
- Select `Worker` as the role.
- Create the worker or app user successfully.
- Use either email or phone where supported by the form.

#### Test General User Actions

After creating the different user types, confirm that QA can test the common user actions from the users table, including:

- Editing a user.
- Deactivating a user.
- Reactivating a user where applicable.
- Deleting a user where that action is allowed.
- Resending an invitation where that action is available.

#### Test The Single User Page

Use the users table to open the single user page.

Confirm that QA can:

- Click a user's name in the users table to open that user's detail page.
- View the account information shown on the page.
- View the organisation information shown on the page where applicable.

Then confirm that QA can test the actions available from the top of the page, depending on the user's state and the permissions of the signed-in tester:

- Invite the user .
- Edit the user from the detail page.
- Deactivate the user.
- Reactivate the user .
- Delete the user.

Also confirm that QA can:

- See the correct user status, including active, inactive, and pending invitation where applicable.
- See the correct organisation, user groups, and role information for the user.
- See the activity log section for the user where activity logs are visible.

### Step 5: Create User Groups

Create one or more user groups for the test organisation.

User groups may represent departments or other organisational groupings.

Confirm that QA can:

- Create a user group as a `58_admin` user.
- Create a user group as an organisation admin.
- Edit a user group.
- See the user group in the relevant table.
- Delete a user group if it is not assigned to any users.

Also confirm that QA can assign a user to user groups in both ways:

- By creating a new user with worker role and assigning the user group during creation.
- By editing an existing worker and adding the user to one or more user groups.

Also confirm the access rules:

- A user can belong to more than one user group.

### Step 6: Create Roles And Permission Sets

Create the roles that will be used by the organisation admin and organisation staff users.

Confirm that QA can:

- Create a role.
- Edit a role.
- Delete a role if allowed.
- Assign permission to a role.
- Remove permission from a role.

Use this step to prepare at least:

- One role with broad organisation-level permissions.
- One more restricted role for staff testing.

### Step 7: Create Work Codes

Create work codes for the test organisation. Work codes will be used to control content accesses by users in the Just Good Work mobile application app users.

Access rule:

- Only a `58_admin` user can create work codes.
- An `org_admin` user can view existing work codes.
- An `org_admin` user can assign a work code to one or more user groups.
- An `org_admin` user can unassign a work code from a user group.

Confirm that QA can:

- Create a work code.
- Edit a work code. Editing the code it self should not be allowed, but other fields can be updated.
- See it appear in the work codes table.
- See qr code for the work code.
- Assign a work code to one or more user groups.
- Unassign a work code from a user group.
- Delete a work code.

Also verify the work code access rules:

- A work code can be assigned to multiple user groups.
- If a work code is assigned to a user group, it cannot be deleted.


### Step 8: Create And Edit Organisation Deep Links

Use the organisation QR Codes links table to test onboarding deep links.

Access rule:

- An `org_admin` user can create organisation deep links.
- An `org_admin` user can view existing organisation deep links.
- An `org_admin` user can open the edit flow for an existing organisation deep link.
- A `58_admin` user can also create, view, and edit organisation deep links.

Confirm that QA can:

- Open the create  link modal.
- Create a deep link.
- See the new deep link in the organisation deep links table.

Then confirm that QA can:
- Open the QR code action for a saved organisation deep link.
- Copy the deep link URL.
- Download the QR code if download actions are available.
- Open the edit action from the row menu.
- See the modal prefilled with existing data.
- Save updates successfully.

### Step 9: Test Bulk Actions On The User Table

Confirm that QA tests the bulk actions available on the users table.

Where available, validate:

- Bulk activation.
- Bulk deactivation.
- Bulk invitation sending.
- Bulk delete.

Also confirm that:

- The correct users are affected.
- Success and error messages are shown correctly.
- The table updates correctly after each bulk action.

### Step 10: Validate Search, Pagination, And UI Behaviour

Across the full module, confirm that QA can successfully use the interface.

Check that:

- Table search works correctly.
- Pagination works correctly.
- Dropdowns populate correctly.
- Custom selects open and allow selection.
- Modals open and close correctly.
- Validation errors display clearly.
- Success messages display correctly.

### Step 11: Validate Audit And Activity Behaviour

Where activity logs or audit trails are expected, confirm that important actions are recorded.

Where to find the logs:

- Open the main User Management page and click `User Activity Logs` in the page header to view the `Recent Activity` page.
- For user-specific checks, open the single user page and review the `Recent Activity` section there.

At minimum, check whether create and update actions are recorded for:

- Organisations.
- Organisation groups.
- Work codes.
- Roles.
- Deep links.
- Users.

