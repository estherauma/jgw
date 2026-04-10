from datetime import datetime, timedelta, timezone
from logging import getLogger

import jwt
from django.conf import settings
from django.urls import reverse
from django.utils import timezone as dj_timezone

from users.models import UserInvitations
from user_management.models import ShortLink
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from users.tasks import send_email_notification
from .sms import send_sms_invitation

logger = getLogger("djangoDebug")


def generate_token(user, invite, days_to_expiry):
    payload = {"exp": datetime.now(tz=timezone.utc) + timedelta(days=days_to_expiry)}
    payload.update({"user_id": user.id, "invite_id": invite.id})
    return jwt.encode(payload=payload, key=settings.SECRET_KEY, algorithm="HS256")


def build_short_link(request, reset_link, days_to_expiry):
    try:
        short_link = ShortLink.create_url_short_link(
            reset_link,
            expires_at=dj_timezone.now() + timedelta(days=days_to_expiry),
        )
        return request.build_absolute_uri(
            reverse("short_link", args=(short_link.code,))
        )
    except Exception as exc:
        logger.error("short link creation failed: %s", exc)
        return reset_link


def build_invitation_context(request, user, days_to_expiry=3, include_short_link=False):
    organisation = user.organisation_data.order_by("created_at").first()
    invite = UserInvitations.objects.create(
        user=user,
        email=user.email,
        organisation=organisation,
        phone_number=user.phone_number,
        status="SENT",
    )
    token = generate_token(user, invite, days_to_expiry)
    reset_link = request.build_absolute_uri(reverse("users:set_password", args=(token,)))
    short_link = (
        build_short_link(request, reset_link, days_to_expiry)
        if include_short_link
        else reset_link
    )
    return {
        "organisation": organisation,
        "invite": invite,
        "reset_link": reset_link,
        "short_link": short_link,
    }


def send_invitation(request, user, days_to_expiry=3):
    if not user or (not user.email and not user.phone_number):
        return False
 
    try:    
        if user.email:
            context = build_invitation_context(
                    request,
                    user,
                    days_to_expiry=days_to_expiry,
                )

            html_content = render_to_string(
                "user_management/invite-user-email.html",
                {
                    "reset_link": context["reset_link"],
                    "organisation_name": context["organisation"].name if context["organisation"] else None,
                },
            )
            message = strip_tags(html_content)
            send_email_notification(
                subject="Set up your account - Just Good Work",
                message=message,
                recipients=[user.email],
                attachment_path=None,
                html_message=html_content,
                inline_images=None,
            )

        else:
            context = build_invitation_context(
                request,
                user,
                days_to_expiry=days_to_expiry,
                include_short_link=True,
            )
            return send_sms_invitation(user, context, days_to_expiry=days_to_expiry)
        
        return True
    except Exception as exc:
        logger.error("send_invitation failed for %s: %s", getattr(user, "email", "unknown"), exc)
        return False
