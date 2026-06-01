from datetime import timedelta
import secrets

import jwt
from django.conf import settings
from django.contrib.auth.hashers import check_password, make_password
from django.db import transaction
from django.template.loader import render_to_string
from django.utils import timezone
from django.utils.html import strip_tags

from common.const.value_const import (
    REGISTRATION_EMAIL_VERIFICATION_PURPOSE,
    REGISTRATION_VERIFICATION_CODE_ALPHABET,
)
from user_management.sms import send_sms
from user_management.utils import normalize_phone_number_for_lookup
from users.models import User, UserVerificationCode
from users.tasks import send_email_notification


ACCESS_TOKEN_MINUTES = 480
REFRESH_TOKEN_DAYS = 30


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
        "users/registration-verification-email.html",
        {
            "user": user,
            "verification_code": verification_code,
            "expiry_minutes": expiry_minutes,
        },
    )
    send_email_notification(
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


def get_registration_user_by_contact(email=None, phone_number=None, phone_country_iso=None, user_id=None):
    normalized_email = (email or "").strip().lower()
    raw_phone_number = (phone_number or "").strip()
    normalized_phone_number = None

    if raw_phone_number:
        normalized_phone_number, phone_error = normalize_phone_number_for_lookup(
            raw_phone_number,
            phone_country_iso,
        )
        if phone_error:
            return None, phone_error

    user_qs = User.all_objects.filter(is_deleted=False)
    if user_id:
        user_qs = user_qs.filter(id=user_id)
    if normalized_email:
        user_qs = user_qs.filter(email__iexact=normalized_email)
    elif normalized_phone_number:
        user_qs = user_qs.filter(phone_number=normalized_phone_number)

    user = user_qs.first()
    if not user:
        return None, "Invalid contact details."
    return user, None


def verify_registration_code(code, email=None, phone_number=None, phone_country_iso=None):
    email = (email or "").strip().lower()
    phone_number = (phone_number or "").strip()
    code = (code or "").strip().upper()
    if (not email and not phone_number) or not code:
        return {
            "ok": False,
            "error": "Either email or phone number and the verification code are required.",
        }

    user, user_error = get_registration_user_by_contact(
        email=email,
        phone_number=phone_number,
        phone_country_iso=phone_country_iso,
    )
    if not user:
        if user_error:
            return {"ok": False, "error": user_error}
        return {"ok": False, "error": "Invalid contact details or verification code."}

    if user.is_active:
        return {"ok": True, "message": "Contact already verified.", "user": user}

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
            from django.contrib.auth.models import Group

            worker_group, _ = Group.objects.get_or_create(name="worker")
            user.groups.add(worker_group)
        user.is_active = True
        user.save(update_fields=["is_active"])
    return {"ok": True, "message": "Verification successful.", "user": user}


def resend_registration_verification_code(email=None, phone_number=None, phone_country_iso=None, user_id=None):
    if not user_id and not email and not phone_number:
        return {
            "ok": False,
            "error": "Provide a user ID, email or phone number.",
        }

    user, user_error = get_registration_user_by_contact(
        email=email,
        phone_number=phone_number,
        phone_country_iso=phone_country_iso,
        user_id=user_id,
    )
    if not user:
        return {
            "ok": False,
            "error": user_error or "Invalid contact details.",
        }

    if user.is_active:
        return {"ok": True, "message": "Contact already verified.", "user": user}

    _, verification_code = create_registration_verification_code(user)
    if user.email:
        send_registration_verification_email(user, verification_code)
    else:
        sms_sent = send_registration_verification_sms(user, verification_code)
        if not sms_sent:
            return {
                "ok": False,
                "error": "Could not send the verification code. Please try again.",
            }

    return {
        "ok": True,
        "message": "A new verification code has been sent.",
        "user": user,
    }


def build_auth_token(user, token_type, expires_at):
    payload = {
        "user_id": user.id,
        "token_type": token_type,
        "exp": expires_at,
        "iat": timezone.now(),
    }
    return jwt.encode(payload=payload, key=settings.SECRET_KEY, algorithm="HS256")


def issue_auth_tokens(user):
    access_expires_at = timezone.now() + timedelta(minutes=ACCESS_TOKEN_MINUTES)
    refresh_expires_at = timezone.now() + timedelta(days=REFRESH_TOKEN_DAYS)
    return {
        "access_token": build_auth_token(user, "access", access_expires_at),
        "refresh_token": build_auth_token(user, "refresh", refresh_expires_at),
        "access_expires_at": access_expires_at,
        "refresh_expires_at": refresh_expires_at,
    }


def login_api_user(email=None, phone_number=None, phone_country_iso=None, password=None):
    normalized_email = (email or "").strip().lower()
    raw_phone_number = (phone_number or "").strip()
    raw_password = password or ""
    if (not normalized_email and not raw_phone_number) or not raw_password:
        return {
            "ok": False,
            "error": "Provide email or phone number, and password.",
        }

    normalized_phone_number = None
    if raw_phone_number:
        normalized_phone_number, phone_error = normalize_phone_number_for_lookup(
            raw_phone_number,
            phone_country_iso,
        )
        if phone_error:
            return {
                "ok": False,
                "error": phone_error,
            }

    user_qs = User.objects.none()
    if normalized_email:
        user_qs = User.objects.filter(email__iexact=normalized_email)
    else:
        user_qs = User.objects.filter(phone_number=normalized_phone_number)
    user = user_qs.first()
    if not user:
        return {
            "ok": False,
            "error": "Invalid login credentials.",
        }

    if not user.check_password(raw_password):
        return {
            "ok": False,
            "error": "Invalid login credentials.",
        }

    if not user.is_active:
        return {
            "ok": False,
            "error": "Account is not active.",
        }

    user.last_login = timezone.now()
    user.save(update_fields=["last_login"])

    return {
        "ok": True,
        "user": user,
        "tokens": issue_auth_tokens(user),
    }


def refresh_api_access_token(refresh_token):
    raw_refresh_token = (refresh_token or "").strip()
    if not raw_refresh_token:
        return {
            "ok": False,
            "error": "Refresh token is required.",
        }

    try:
        payload = jwt.decode(raw_refresh_token, settings.SECRET_KEY, algorithms=["HS256"])
    except jwt.ExpiredSignatureError:
        return {
            "ok": False,
            "error": "Refresh token has expired.",
        }
    except jwt.InvalidTokenError:
        return {
            "ok": False,
            "error": "Invalid refresh token.",
        }

    if payload.get("token_type") != "refresh":
        return {
            "ok": False,
            "error": "Invalid refresh token.",
        }

    user = User.objects.filter(id=payload.get("user_id"), is_deleted=False).first()
    if not user:
        return {
            "ok": False,
            "error": "Invalid refresh token.",
        }
    if not user.is_active:
        return {
            "ok": False,
            "error": "Account is not active.",
        }

    return {
        "ok": True,
        "user": user,
        "tokens": issue_auth_tokens(user),
    }
