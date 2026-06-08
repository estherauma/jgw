from datetime import timedelta
import secrets

import jwt
from django.conf import settings
from django.contrib.auth.hashers import check_password, make_password
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import transaction
from django.template.loader import render_to_string
from django.utils import timezone
from django.utils.html import strip_tags

from common.const.value_const import (
    REGISTRATION_EMAIL_VERIFICATION_PURPOSE,
    REGISTRATION_VERIFICATION_CODE_ALPHABET,
)
from common.services.audit import AuditService
from user_management.sms import send_sms
from user_management.utils import normalize_phone_number_for_lookup
from users.models import User, UserVerificationCode
from users.tasks import send_email_notification


ACCESS_TOKEN_MINUTES = 480
REFRESH_TOKEN_DAYS = 30
PASSWORD_RESET_VERIFICATION_PURPOSE = "password_reset"
PASSWORD_RESET_GENERIC_MESSAGE = (
    "If an account exists for the provided contact details, a password reset code has been sent."
)


def generate_registration_verification_code(length=6):
    return "".join(
        secrets.choice(REGISTRATION_VERIFICATION_CODE_ALPHABET)
        for _ in range(length)
    )


def create_user_verification_code(
    user,
    purpose,
    expires_in_minutes=15,
    max_attempts=3,
):
    code = generate_registration_verification_code()
    expires_at = timezone.now() + timedelta(minutes=expires_in_minutes)
    UserVerificationCode.objects.filter(
        user=user,
        purpose=purpose,
        used_at__isnull=True,
    ).delete()
    verification = UserVerificationCode.objects.create(
        user=user,
        purpose=purpose,
        code_hash=make_password(code),
        expires_at=expires_at,
        max_attempts=max_attempts,
    )
    return verification, code


def send_code_email(user, verification_code, template_name, subject, expiry_minutes=15):
    html_message = render_to_string(
        template_name,
        {
            "user": user,
            "verification_code": verification_code,
            "expiry_minutes": expiry_minutes,
        },
    )
    send_email_notification(
        subject=subject,
        message=strip_tags(html_message),
        recipients=[user.email],
        attachment_path=None,
        html_message=html_message,
        inline_images=None,
    )


def send_code_sms(
    user,
    message,
):
    if not user.phone_number:
        return False
    return send_sms(user.phone_number, message)


def get_user_by_contact(email=None, phone_number=None, phone_country_iso=None, user_id=None):
    normalized_email = (email or "").strip().lower()
    raw_phone_number = (phone_number or "").strip()
    normalized_phone_number = None

    if raw_phone_number:
        normalized_phone_number, phone_error = normalize_phone_number_for_lookup(
            raw_phone_number,
            phone_country_iso,
        )
        print("Normalized phone number:", normalized_phone_number)  
        if phone_error:
            return None, phone_error

    user_qs = User.objects.all()
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

    user, user_error = get_user_by_contact(
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

    user, user_error = get_user_by_contact(
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

    _, verification_code = create_user_verification_code(
        user,
        REGISTRATION_EMAIL_VERIFICATION_PURPOSE,
    )
    if user.email:
        send_code_email(
            user,
            verification_code,
            "users/registration-verification-email.html",
            "Verify your email - Just Good Work",
        )
    else:
        sms_sent = send_code_sms(
            user,
            f"Your Just Good Work verification code is {verification_code}. "
            f"It expires in 15 minutes.",
        )
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


def request_password_reset_code(email=None, phone_number=None, phone_country_iso=None):
    if not email and not phone_number:
        return {
            "ok": False,
            "error": "Provide email or phone number.",
        }

    user, user_error = get_user_by_contact(
        email=email,
        phone_number=phone_number,
        phone_country_iso=phone_country_iso,
    )
    if user_error and user_error != "Invalid contact details.":
        return {
            "ok": False,
            "error": user_error,
        }
    
    if not user:
        return {"ok": False, "error": 'Something went wrong. Please try again.'}

    if not user.is_active:
        return {"ok": False, "error": "Account is not active."}

    _, verification_code = create_user_verification_code(
        user,
        PASSWORD_RESET_VERIFICATION_PURPOSE,
    )
    if user.email:
        send_code_email(
            user,
            verification_code,
            "users/password-reset-code-email.html",
            "Reset your password - Just Good Work",
        )
    else:
        sms_sent = send_code_sms(
            user,
            f"Your Just Good Work password reset code is {verification_code}. "
            f"It expires in 15 minutes.",
        )
        print("Password reset SMS sent:", sms_sent)
        if not sms_sent:
            return {
                "ok": False,
                "error": "Could not send the password reset code. Please try again.",
            }

    return {"ok": True, "message": PASSWORD_RESET_GENERIC_MESSAGE}


def verify_password_reset_code(
    code,
    email=None,
    phone_number=None,
    phone_country_iso=None,
):
    normalized_code = (code or "").strip().upper()

    if (not email and not phone_number) or not normalized_code:
        return {
            "ok": False,
            "error": "Provide email or phone number, and the reset code.",
        }

    user, user_error = get_user_by_contact(
        email=email,
        phone_number=phone_number,
        phone_country_iso=phone_country_iso,
    )
    if not user:
        return {
            "ok": False,
            "error": user_error or "Invalid contact details or reset code.",
        }

    if not user.is_active:
        return {"ok": False, "error": "Account is not active."}

    verification = (
        UserVerificationCode.objects.filter(
            user=user,
            purpose=PASSWORD_RESET_VERIFICATION_PURPOSE,
            used_at__isnull=True,
        )
        .order_by("-created_at")
        .first()
    )
    if not verification:
        return {"ok": False, "error": "No active password reset code was found."}

    if verification.is_expired():
        return {"ok": False, "error": "This password reset code has expired."}

    if verification.attempts >= verification.max_attempts:
        return {
            "ok": False,
            "error": "This password reset code has been locked. Request a new code.",
        }

    if not check_password(normalized_code, verification.code_hash):
        verification.attempts += 1
        verification.save(update_fields=["attempts"])
        if verification.attempts >= verification.max_attempts:
            return {
                "ok": False,
                "error": "This password reset code has been locked. Request a new code.",
            }
        return {"ok": False, "error": "Invalid contact details or reset code."}

    return {"ok": True, "user": user}


def reset_password_with_code(code, password, email=None, phone_number=None, phone_country_iso=None):
    normalized_code = (code or "").strip().upper()

    if (not email and not phone_number) or not normalized_code:
        return {
            "ok": False,
            "error": "Provide email or phone number, and the reset code.",
        }

    if not password:
        return {"ok": False, "error": "Password is required."}

    user, user_error = get_user_by_contact(
        email=email,
        phone_number=phone_number,
        phone_country_iso=phone_country_iso,
    )
    if not user:
        return {
            "ok": False,
            "error": user_error or "Invalid contact details or reset code.",
        }

    if not user.is_active:
        return {"ok": False, "error": "Account is not active."}
    
    verification = (
        UserVerificationCode.objects.filter(
            user=user,
            purpose=PASSWORD_RESET_VERIFICATION_PURPOSE,
            used_at__isnull=True,
        )
        .order_by("-created_at")
        .first()
    )
    if not verification:
        return {"ok": False, "error": "No active password reset code was found."}

    if verification.is_expired():
        return {"ok": False, "error": "This password reset code has expired."}

    if verification.attempts >= verification.max_attempts:
        return {
            "ok": False,
            "error": "This password reset code has been locked. Request a new code.",
        }

    if not check_password(normalized_code, verification.code_hash):
        verification.attempts += 1
        verification.save(update_fields=["attempts"])
        if verification.attempts >= verification.max_attempts:
            return {
                "ok": False,
                "error": "This password reset code has been locked. Request a new code.",
            }
        return {"ok": False, "error": "Invalid contact details or reset code."}

    try:
        validate_password(password, user=user)
    except DjangoValidationError as exc:
        return {"ok": False, "error": exc.messages[0]}

    with transaction.atomic():
        verification.used_at = timezone.now()
        verification.save(update_fields=["used_at"])
        UserVerificationCode.objects.filter(
            user=user,
            purpose=PASSWORD_RESET_VERIFICATION_PURPOSE,
            used_at__isnull=True,
        ).exclude(pk=verification.pk).delete()
        user.set_password(password)
        user.save()
        AuditService.log_action(instance=user, action="password_reset")

    return {"ok": True, "user": user}


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
