from datetime import datetime, timedelta, timezone

import jwt
from django.conf import settings
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.html import strip_tags
from django.core.mail import EmailMultiAlternatives, send_mail
from email.mime.image import MIMEImage
import mimetypes
import os

from users.models import UserInvitations
from users.tasks import send_email_notification

def send_invitation(request, user, days_to_expiry=3):

    if not user or not user.email:
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
        html_content = render_to_string(
            "user_management/invite-user-email.html",
            {
                "reset_link": reset_link,
                "organisation_name": organisation.name if organisation else None,
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
        return True
    except Exception as exc:
        print(f"send_invitation failed for {getattr(user, 'email', 'unknown')}: {exc}")
        return False
