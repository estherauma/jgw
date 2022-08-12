from logging import getLogger

from celery import shared_task
from django.core.mail import EmailMessage, send_mail

from users.models import User

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
    debug_logger.debug(f"recipients:{recipients}")
    subject = "Inactive User Accounts"
    body = (
        f"The following user accounts have been created and need to be activated:\n"
        f"{inactive_users}"
        f"\n\n JGWPandas"
    )
    send_mail(
        subject=subject, message=body, from_email="alerts@jgwpandas.herokuapp.com", recipient_list=recipients
    )


@shared_task(name="send_email_notification")
def send_email_notification(subject, message, recipients, attachment_path=None):
    mail = EmailMessage(subject, message, "alerts@jgwpandas.herokuapp.com", recipients)
    if attachment_path:
        mail.attach_file(attachment_path)
    mail.send()
