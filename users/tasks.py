from logging import getLogger
from celery import shared_task
from django.core.mail import EmailMultiAlternatives, send_mail
from users.models import User
from email.mime.image import MIMEImage
import os
import mimetypes

debug_logger = getLogger("djangoDebug")

@shared_task(name="notify_admins_inactive_users")
def notify_admins_inactive_users():
    inactive_users = User.objects.filter(is_active=False).values_list("email")
    if not inactive_users:
        return
    inactive_users = [i[0] for i in inactive_users]
    inactive_users = "\n".join(inactive_users)
    recipients = User.objects.filter(is_superuser=True).values_list("email")
    recipients = [i[0] for i in recipients]
    subject = "Inactive User Accounts"
    body = (
        f"The following user accounts have been created and need to be activated:\n"
        f"{inactive_users}"
        f"\n\n JGWPandas"
    )
    send_mail(
        subject=subject, message=body, from_email="JGW Pandas <alerts@jgwpandas.com>", recipient_list=recipients
    )


@shared_task(name="send_email_notification")
def send_email_notification(subject, message, recipients, attachment_path=None, html_message=None, inline_images=None):
    """
    Sends an email with optional HTML content, attachments, and inline images.
    
    :param subject: Email subject
    :param message: Plain text fallback
    :param recipients: List of recipient email addresses
    :param html_message: HTML formatted email content
    :param attachment_path: File path of an attachment (if any)
    :param inline_images: Dict {CID: file_path} for inline images
    """
    try:
        mail = EmailMultiAlternatives(
            subject,
            message,
            "JGW Pandas <alerts@jgwpandas.com>",
            recipients,
        )

        if attachment_path:
            mail.attach_file(attachment_path)

        if html_message:
            mail.attach_alternative(html_message, "text/html")

        if inline_images:
            for cid, img_path in inline_images.items():
                if os.path.exists(img_path):
                    mime_type, _ = mimetypes.guess_type(img_path)
                    if not mime_type:
                        mime_type = "../static/logo.jpeg"

                    with open(img_path, "rb") as img_file:
                        image = MIMEImage(img_file.read(), _subtype=mime_type.split("/")[-1])
                        image.add_header("Content-ID", f"<{cid}>")
                        image.add_header(
                            "Content-Disposition",
                            "inline",
                            filename=os.path.basename(img_path),
                        )
                        mail.attach(image)

        mail.send()
    except Exception as exc:
        debug_logger.exception("send_email_notification failed: %s", exc)
