from datetime import datetime, timedelta, timezone
from logging import getLogger

import jwt
from django.conf import settings
from django.urls import reverse
from twilio.rest import Client

from users.models import UserInvitations

logger = getLogger("djangoDebug")


def send_sms_invitation(request, user, days_to_expiry=3):
    if not user or not user.phone_number:
        return False
    

    account_sid = getattr(settings, "TWILIO_ACCOUNT_SID", None)
    auth_token = getattr(settings, "TWILIO_AUTH_TOKEN", None)
    from_number = getattr(settings, "TWILIO_FROM_NUMBER", None)
    if not account_sid or not auth_token or not from_number:
        print("printing: Twilio credentials are not configured.")
        logger.error("Twilio credentials are not configured.")
        return False

    try:
        organisation = user.organisation_data.order_by("created_at").first()
        invite = UserInvitations.objects.create(
            user=user,
            email=user.email,
            organisation=organisation,
            phone_number=user.phone_number,
            status="SENT",
        )
        payload = {"exp": datetime.now(tz=timezone.utc) + timedelta(days=days_to_expiry)}
        payload.update({"user_id": user.id, "invite_id": invite.id})
        token = jwt.encode(payload=payload, key=settings.SECRET_KEY, algorithm="HS256")
        reset_link = request.build_absolute_uri(
            reverse("users:set_password", args=(token,))
        )
        org_text = f"You have been added to {organisation.name}. " if organisation else ""
        message = (
            f"{org_text}Set your password to finish setup: {reset_link} "
            f"This link expires in {days_to_expiry} days."
        )
        client = Client(account_sid, auth_token)
        params = {"body": message, "to": user.phone_number, "from_": '+12602691402'} 
  
        client.messages.create(**params)
        return True
    except Exception as exc:
        print(f"send_sms_invitation failed for {user.phone_number}: {exc}")
        logger.exception("send_invitation sms failed for %s: %s", user.phone_number, exc)
        return False
