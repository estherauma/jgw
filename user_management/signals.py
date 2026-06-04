import logging

from django.db.models.signals import pre_save, post_save, pre_delete
from django.dispatch import receiver

from preference.models import OrganisationData
from user_management.services.activity import UserActivityService

logger = logging.getLogger(__name__)


@receiver(pre_save, sender=OrganisationData)
def capture_organisation_before_state(sender, instance, **kwargs):
    if not instance.pk:
        return
    try:
        db_current = sender.objects.get(pk=instance.pk)
        instance._pre_save_state = UserActivityService.organisation_state(db_current)
    except sender.DoesNotExist:
        instance._pre_save_state = {}


@receiver(post_save, sender=OrganisationData)
def log_organisation_activity(sender, instance, created, **kwargs):
    if created:
        UserActivityService.log_organisation_created(
            actor=getattr(instance, "created_by", None),
            organisation=instance,
        )
    else:
        before_state = getattr(instance, "_pre_save_state", {})
        after_state = UserActivityService.organisation_state(instance)
        changes = UserActivityService.build_changes(before_state, after_state)
        message = UserActivityService._build_update_message(instance.name, changes)
        UserActivityService.log_action(
            actor=getattr(instance, "updated_by", None),
            action="updated",
            record_type=UserActivityService.ORGANISATION_RECORD_TYPE,
            record_id=str(instance.id),
            organisation=instance,
            message=message,
            changes=changes,
        )


@receiver(pre_delete, sender=OrganisationData)
def log_organisation_delete(sender, instance, **kwargs):
    before_state = UserActivityService.organisation_state(instance)
    UserActivityService.log_organisation_deleted(
        actor=getattr(instance, "deleted_by", None) or getattr(instance, "updated_by", None),
        organisation_id=instance.id,
        organisation_name=instance.name,
        organisation=None,
        before_state=before_state,
    )
