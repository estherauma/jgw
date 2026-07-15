from django.db import transaction

from users.models import UserVerificationCode


@transaction.atomic
def anonymize_and_soft_delete_user(user):
    user.email = f"deleted-{user.id}@deleted.local"
    user.first_name = ""
    user.last_name = ""
    user.phone_number = None
    user.phone_country_iso = None
    user.start_date = None
    user.end_date = None
    user.receive_marketing_emails = False
    user.dashboard_preferences = {}
    user.set_unusable_password()
    user.soft_delete(deleted_by=user)

    UserVerificationCode.objects.filter(user=user).delete()

    return user
