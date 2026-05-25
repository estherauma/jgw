from datetime import timedelta
import secrets

from django.contrib.auth.models import Group
from django.contrib.auth.hashers import check_password, make_password
from django.db import transaction
from django.template.loader import render_to_string
from django.utils import timezone
from django.utils.html import strip_tags

from common.const.value_const import (
    REGISTRATION_EMAIL_VERIFICATION_PURPOSE,
    REGISTRATION_VERIFICATION_CODE_ALPHABET,
)
from users.models import User, UserInvitations
from users.tasks import send_email_notification
from user_management.models import UserVerificationCode, WorkGroup
from user_management.sms import send_sms

from user_management.services.organization import OrganizationService
from user_management.roles import add_default_org_roles, apply_role_to_user
from user_management.utils import (
    get_active_role,
    get_group_names,
    is_org_admin_or_staff,
    is_org_group_admin,
    is_super_or_58_admin,
)


def generate_registration_verification_code(length=6):
    return "".join(
        secrets.choice(REGISTRATION_VERIFICATION_CODE_ALPHABET)
        for _ in range(length)
    )


def create_registration_verification_code(
    user,
    expires_in_minutes=15,
    max_attempts=3,
):
    code = generate_registration_verification_code()
    expires_at = timezone.now() + timedelta(minutes=expires_in_minutes)
    UserVerificationCode.objects.filter(
        user=user,
        purpose=REGISTRATION_EMAIL_VERIFICATION_PURPOSE,
        used_at__isnull=True,
    ).delete()
    verification = UserVerificationCode.objects.create(
        user=user,
        purpose=REGISTRATION_EMAIL_VERIFICATION_PURPOSE,
        code_hash=make_password(code),
        expires_at=expires_at,
        max_attempts=max_attempts,
    )
    return verification, code


def send_registration_verification_email(
    user,
    verification_code,
    expiry_minutes=15,
):
    html_message = render_to_string(
        "user_management/registration-verification-email.html",
        {
            "user": user,
            "verification_code": verification_code,
            "expiry_minutes": expiry_minutes,
        },
    )
    send_email_notification.delay(
        subject="Verify your email - Just Good Work",
        message=strip_tags(html_message),
        recipients=[user.email],
        attachment_path=None,
        html_message=html_message,
        inline_images=None,
    )


def send_registration_verification_sms(
    user,
    verification_code,
    expiry_minutes=15,
):
    if not user.phone_number:
        return False
    message = (
        f"Your Just Good Work verification code is {verification_code}. "
        f"It expires in {expiry_minutes} minutes."
    )
    return send_sms(user.phone_number, message)


def assign_default_app_registration_membership(user, organisation):
    add_default_org_roles(organisation)
    worker_role = organisation.roles.filter(name__iexact="Worker").first()
    if not worker_role:
        raise ValueError("Default Worker role was not found for this organisation.")

    worker_work_group, _ = WorkGroup.objects.get_or_create(
        organisation=organisation,
        name="Worker",
    )
    user.organisation_data.add(organisation)
    apply_role_to_user(user, organisation, worker_role)
    user.work_groups.add(worker_work_group)
    return {"role": worker_role, "work_group": worker_work_group}


def verify_registration_code(submitted_code, email=None, phone_number=None):
    email = (email or "").strip().lower()
    phone_number = (phone_number or "").strip()
    code = (submitted_code or "").strip().upper()
    if (not email and not phone_number) or not code:
        return {
            "ok": False,
            "error": "Either email or phone number and the verification code are required.",
        }

    user_qs = User.all_objects.filter(is_deleted=False)
    if email:
        user_qs = user_qs.filter(email__iexact=email)
    else:
        user_qs = user_qs.filter(phone_number=phone_number)
    user = user_qs.first()
    if not user:
        return {"ok": False, "error": "Invalid contact details or verification code."}

    if user.is_active:
        return {"ok": True, "message": "Email already verified.", "user": user}

    verification = (
        UserVerificationCode.objects.filter(
            user=user,
            purpose=REGISTRATION_EMAIL_VERIFICATION_PURPOSE,
            used_at__isnull=True,
        )
        .order_by("-created_at")
        .first()
    )
    if not verification:
        return {"ok": False, "error": "No active verification code was found."}

    if verification.is_expired():
        return {"ok": False, "error": "This verification code has expired."}

    if verification.attempts >= verification.max_attempts:
        return {"ok": False, "error": "This verification code has been locked. Request a new code."}

    if not check_password(code, verification.code_hash):
        verification.attempts += 1
        verification.save(update_fields=["attempts"])
        if verification.attempts >= verification.max_attempts:
            return {"ok": False, "error": "This verification code has been locked. Request a new code."}
        return {"ok": False, "error": "Invalid contact details or verification code."}

    with transaction.atomic():
        verification.used_at = timezone.now()
        verification.save(update_fields=["used_at"])
        if user.access_type == "app":
            worker_group, _ = Group.objects.get_or_create(name="worker")
            user.groups.add(worker_group)
        user.is_active = True
        user.save(update_fields=["is_active"])
    return {"ok": True, "message": "Email verified successfully.", "user": user}


def get_user_role_display(user, selected_org=None):
    role = get_active_role(user)
    if role == "super_user":
        return "Super Admin"
    if role == "58_admin":
        return "Fiftyeight Admin"
    if role == "org_group_admin":
        return "Organization Group Admin"
    if role == "org_admin":
        return "Administrator" if selected_org else "Org Admin"
    if role == "org_staff":
        assignment = user.org_roles.all().first()
        if assignment and assignment.role:
            return assignment.role.name
    if "worker" in get_group_names(user):
        return "Worker"
    return "—"


def get_users_query(current_user, selected_org=None):
    users = (
        User.objects.prefetch_related(
            "groups",
            "organisation_data",
            "work_groups",
            "org_roles__role",
            "org_roles__organisation",
        )
        .select_related("organization_group")
        .order_by("-created_at")
        .distinct()
    )
    if selected_org:
        users = users.filter(organisation_data=selected_org)

    if is_org_admin_or_staff(current_user):
        allowed_orgs = OrganizationService.get_allowed_orgs(current_user)
        users = users.filter(organisation_data__in=allowed_orgs).distinct()
    for user in users:
        user.role_display = get_user_role_display(user, selected_org=selected_org)
        user.organisation_display = (
            user.organization_group.name
            if is_org_group_admin(user) and user.organization_group
            else ", ".join(user.organisation_data.values_list("name", flat=True)) or "—"
        )
        user.hide_organisation_information = is_super_or_58_admin(user)
        user.has_pending_invitation = UserInvitations.objects.filter(
            user=user,
            status__in=["SENT", "PENDING"],
        ).exists()

    return users
