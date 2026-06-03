from django.db.models.signals import m2m_changed, post_save, pre_delete, pre_save
from django.dispatch import receiver

from common.services.audit import AuditService


def _get_m2m_field_name(instance, through_model):
    for field in instance._meta.many_to_many:
        if field.remote_field.through is through_model:
            return field.name

    for relation in instance._meta.related_objects:
        if relation.many_to_many and relation.field.remote_field.through is through_model:
            return relation.get_accessor_name()
    return None


@receiver(pre_save)
def capture_model_before_state(sender, instance, **kwargs):
    if not AuditService.should_track_instance(instance):
        return
    if not instance.pk:
        return

    try:
        db_current = AuditService.get_manager(sender).get(pk=instance.pk)
        instance._pre_save_state = AuditService.serialize_state(db_current)
    except sender.DoesNotExist:
        instance._pre_save_state = {}


@receiver(post_save)
def log_model_activity(sender, instance, created, **kwargs):
    if not AuditService.should_track_instance(instance):
        return

    before_state = {} if created else getattr(instance, "_pre_save_state", {})
    after_state = AuditService.serialize_state(instance)
    action = AuditService.resolve_action(
        instance=instance,
        created=created,
        before=before_state,
        after=after_state,
    )
    if not AuditService.should_track_instance(instance, action):
        return

    changes = (
        {"before": {}, "after": after_state}
        if created
        else AuditService.build_changes(before_state, after_state)
    )

    if not created and action == "updated" and not AuditService.has_changes(changes):
        return

    AuditService.log_action(
        instance=instance,
        action=action,
        changes=changes,
        message=AuditService.build_state_change_message(
            instance=instance,
            action=action,
            before=before_state,
            after=after_state,
        ),
    )


@receiver(pre_delete)
def log_model_delete(sender, instance, **kwargs):
    if not AuditService.should_track_instance(instance):
        return

    before_state = AuditService.serialize_state(instance)
    AuditService.log_action(
        instance=instance,
        action=AuditService.resolve_action(
            instance=instance,
            hard_delete=True,
            before=before_state,
            after={},
        ),
        changes={"before": before_state, "after": {}},
    )


@receiver(m2m_changed)
def log_many_to_many_activity(sender, instance, action, reverse, model, pk_set, **kwargs):
    if action not in {"post_add", "post_remove", "post_clear"}:
        return
    if not AuditService.should_track_instance(instance):
        return

    relation_name = _get_m2m_field_name(instance, sender)
    if not relation_name:
        return

    audit_action = AuditService.resolve_m2m_action(instance, relation_name, action)
    if not audit_action:
        return

    related_ids = sorted(pk_set) if pk_set else []
    changes = {
        "before": {},
        "after": {
            "relation": relation_name,
            "related_model": model._meta.label_lower,
            "related_ids": related_ids,
            "operation": action,
        },
    }

    AuditService.log_action(
        instance=instance,
        action=audit_action,
        changes=changes,
        message=AuditService.build_m2m_message(
            instance,
            relation_name,
            audit_action,
            related_model=model,
            related_ids=related_ids,
        ),
    )
