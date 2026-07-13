from logging import getLogger

from django.conf import settings
from twilio.rest import Client

logger = getLogger("djangoDebug")


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
            "body": message,
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
            f"You have been added to {context['organisation'].name}. "
            if context["organisation"]
            else ""
        )
        message = (
            f"{org_text} Click the link to set your password and finish setup: {context['short_link']} "
            f"This link expires in {days_to_expiry} days."
        )
        logger.info("Sending SMS to %s: %s", user.phone_number, message)
        return send_sms(user.phone_number, message)
    except Exception as exc:
        logger.exception("send_sms_invitation failed for %s: %s", user.phone_number, exc)
        return False
