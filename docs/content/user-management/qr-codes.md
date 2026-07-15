## QR Codes

We use [Branch.io](https://branch.io/) to create the deep links behind QR codes, and each QR code is attached to a Branch link. After Branch generates the URL, we save it in our database:

- Login QR code URLs are saved on the `OrganisationAccessCode` table in the `deep_link` field.
- Onboarding QR code URLs are saved on the `OrganisationDeepLink` table in the `link` field.

### Purpose

This page explains how QR codes are used inside User Management.

QR codes in this module are used as entry points into mobile login or onboarding flows.

### QR Code Types

We currently have two QR-code types in User Management:

- Login QR codes
- Onboarding QR codes

### Login QR Codes

Login QR codes are opened from the action menu in the **Work Codes** table.

They are used for the login flow of a specific work code.

They:

- represent a login deep link for a specific work code
- help users open the mobile flow associated with that work code
- allow an authorised user to copy the link
- allow an authorised user to download the QR code

Who can create them:

- superusers
- `58_admin` users
- organisation users who have permission to generate login QR codes for that organisation

How they are created:

- A user opens the `QR code` action from a work code row.
- The dashboard sends a request to create or fetch the login deep link for that work code.
- If the work code already has a saved deep link, that link is reused.
- If it does not have one yet, the system creates a **Branch** login deep link and saves it on the work code.
- The system then generates the QR code from that deep-link URL and shows it in the modal.

### Onboarding QR Codes

Onboarding QR codes are opened from the **Organisation QR Codes** table.

They are used for saved organisation onboarding deep links.

They:

- represent a saved onboarding deep link for the selected organisation
- support sharing onboarding flows outside the dashboard
- allow an authorised user to copy the saved link
- allow an authorised user to download the QR code 

Who can create them:

- superusers
- `58_admin` users
- organisation users who have permission to create organisation deep links for that organisation

How they are created:

- A user clicks `Create link` in the **Organisation QR Codes** section.
- The user fills in the onboarding deep-link form and saves it.
- The system creates a Branch onboarding deep link and stores it as an organisation deep-link record.
- After the link exists in the table, the user can open the `QR code` action for that saved deep link.
- The QR code is generated from the saved deep-link URL and shown in the modal.



### Related Docs

- [User Management Overview](../overview/)
- [Organisation Workflow](../organisation-workflow/)
- [QA Guide](../qa-guide/)
- [Work Codes](../work-codes)
