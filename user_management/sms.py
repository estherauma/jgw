from logging import getLogger

from django.conf import settings
from twilio.rest import Client

logger = getLogger("djangoDebug")
SMS_OPT_OUT_TEXT = "Reply STOP to opt out."


def build_sms_body(message):
    if message.endswith(SMS_OPT_OUT_TEXT):
        return message
    return f"{message} {SMS_OPT_OUT_TEXT}"


def send_sms(to_number, message):
    account_sid = getattr(settings, "TWILIO_ACCOUNT_SID", None)
    auth_token = getattr(settings, "TWILIO_AUTH_TOKEN", None)
    messaging_service_sid = getattr(settings, "TWILIO_MESSAGING_SERVICE_SID", None)
    if not account_sid or not auth_token or not messaging_service_sid:
        logger.error("Twilio credentials or messaging service SID are not configured.")
        return False
    try:
        client = Client(account_sid, auth_token)
        params = {
            "body": build_sms_body(message),
            "to": to_number,
            "messaging_service_sid": messaging_service_sid,
        }
        client.messages.create(**params)
        return True
    except Exception as exc:
        logger.exception("send_sms failed for %s: %s", to_number, exc)
        return False


def send_sms_invitation(user, context, days_to_expiry=3):
    if not getattr(settings, "VERIFY_PHONE_NUMBER", False):
        return False
    if not user or not user.phone_number:
        return False

    try:
        org_text = (
            f"Your organization {context['organisation'].name} has created an account for you. "
            if context["organisation"]
            else "An account has been created for you. "
        )
        message = (
            f"Just Good Work: {org_text}Your temporary password is "
            f"{context['temporary_password']}. It expires in "
            f"{context['temporary_password_expiry_days']} days. "
            f"Log in using your phone number."
        )

        last_3 = (user.phone_number or "")[-3:]
        logger.info("Sending SMS to number ending in %s", last_3)
        return send_sms(user.phone_number, message)
    except Exception as exc:
        logger.exception("send_sms_invitation failed for number ending with %s: %s", last_3, exc)
        return False
