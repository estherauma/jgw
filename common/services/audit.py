import logging
from datetime import date, datetime
from decimal import Decimal

from django.db import connection
from django.db import models
from django.forms.models import model_to_dict

from preference.models import OrganisationData, OrganizationGroup
from user_management.models import UserActivity
from users.models import User, UserInvitations

logger = logging.getLogger(__name__)


class AuditService:
    USER_ACTIVITY_TABLE = "user_management_useractivity"
    TRACKED_MODELS = {
        "preference.organisationdata",
        "preference.organizationgroup",
        "preference.organisationaccesscode",
        "user_management.workgroup",
        "user_management.organisationrole",
        "user_management.organisationrolepermission",
        "users.user",
        "users.userinvitations",
    }
    IGNORED_CHANGE_FIELDS = {
        "last_cms_sync_date",
    }
    M2M_ACTION_RULES = {
        ("user_management.workgroup", "access_codes", "post_add"): "assigned",
        ("user_management.workgroup", "access_codes", "post_remove"): "unassigned",
        ("user_management.workgroup", "access_codes", "post_clear"): "unassigned",
        ("preference.organisationaccesscode", "work_groups", "post_add"): "assigned",
        ("preference.organisationaccesscode", "work_groups", "post_remove"): "unassigned",
        ("preference.organisationaccesscode", "work_groups", "post_clear"): "unassigned",
        ("users.user", "organisation_data", "post_add"): "assigned",
        ("users.user", "organisation_data", "post_remove"): "unassigned",
        ("users.user", "organisation_data", "post_clear"): "unassigned",
        ("users.user", "work_groups", "post_add"): "assigned",
        ("users.user", "work_groups", "post_remove"): "unassigned",
        ("users.user", "work_groups", "post_clear"): "unassigned",
    }
    ACTIONS_WITHOUT_CHANGES = {"assigned", "unassigned", "deleted", "invited", "password_reset"}



    @classmethod
    def normalize_value(cls, value):
        if isinstance(value, models.Model):
            return value.pk
        if hasattr(value, "all") and callable(getattr(value, "all")):
            return [cls.normalize_value(item) for item in value.all()]
        if isinstance(value, (datetime, date)):
            return value.isoformat()
        if isinstance(value, Decimal):
            return str(value)
        if isinstance(value, dict):
            return {str(key): cls.normalize_value(item) for key, item in value.items()}
        if isinstance(value, (list, tuple, set)):
            return [cls.normalize_value(item) for item in value]
        return value

    @classmethod
    def get_manager(cls, model_class):
        return getattr(model_class, "all_objects", model_class._default_manager)

    @classmethod
    def get_record_type(cls, instance):
        return getattr(instance, "audit_record_type", instance._meta.model_name)

    @classmethod
    def should_track_instance(cls, instance, action=None):
        if instance._meta.label_lower not in cls.TRACKED_MODELS:
            return False
        if action is None:
            return True
        if instance._meta.label_lower == "user_management.organisationrolepermission":
            return action in {"created", "deleted"}
        if instance._meta.label_lower == "users.userinvitations":
            return action == "invited"
        if instance._meta.label_lower == "preference.organisationdata":
            return action in {
                "created",
                "updated",
                "deleted",
                "assigned",
                "unassigned",
            }
        return action in {"created", "updated", "deleted", "activated", "deactivated"}

    @classmethod
    def serialize_state(cls, instance, extra_state=None):
        if not instance:
            return {}

        state_data = model_to_dict(instance)
        extra_state = extra_state or {}
        state_data.update(extra_state)
        return {key: cls.normalize_value(value) for key, value in state_data.items()}

    @classmethod
    def build_changes(cls, before=None, after=None):
        before = before or {}
        after = after or {}
        changed_before = {}
        changed_after = {}

        for key in sorted(set(before.keys()) | set(after.keys())):
            if key in cls.IGNORED_CHANGE_FIELDS:
                continue
            before_value = before.get(key)
            after_value = after.get(key)
            if before_value != after_value:
                changed_before[key] = before_value
                changed_after[key] = after_value

        return {
            "before": changed_before,
            "after": changed_after,
        }

    @classmethod
    def has_changes(cls, changes):
        return bool((changes or {}).get("after"))

    @classmethod
    def resolve_action(cls, *, instance, created=False, hard_delete=False, before=None, after=None):
        before = before or {}
        after = after or {}
        if instance._meta.label_lower == "users.userinvitations":
            if after.get("status") == "SENT" and before.get("status") != "SENT":
                return "invited"
            return "created" if created else "updated"
        if (
            instance._meta.label_lower == "preference.organisationdata"
            and before.get("organization_group") != after.get("organization_group")
        ):
            if before.get("organization_group") is None and after.get("organization_group") is not None:
                return "assigned"
            if before.get("organization_group") is not None and after.get("organization_group") is None:
                return "unassigned"
        if created:
            return "created"
        if hard_delete:
            return "deleted"
        if before.get("is_deleted") is False and after.get("is_deleted") is True:
            return "deleted"
        if before.get("is_active") is True and after.get("is_active") is False:
            return "deactivated"
        if before.get("is_active") is False and after.get("is_active") is True:
            return "activated"
        return "updated"

    @classmethod
    def build_message(cls, action, instance):
        if action == "password_reset" and isinstance(instance, User):
            return f'Reset password for user "{cls.get_instance_label(instance)}"'
        if instance._meta.label_lower == "user_management.organisationrolepermission":
            permission_name = getattr(getattr(instance, "flag", None), "name", "")
            role_name = getattr(getattr(instance, "role", None), "name", "")
            organisation_name = getattr(getattr(getattr(instance, "role", None), "organisation", None), "name", "")
            if action == "created":
                return f'Added permission "{permission_name}" to role "{role_name}" in {organisation_name}'
            if action == "deleted":
                return f'Removed permission "{permission_name}" from role "{role_name}" in {organisation_name}'
        if instance._meta.label_lower == "users.userinvitations" and action == "invited":
            return f'Invited user "{cls.get_instance_label(instance)}"'
        object_name = instance._meta.verbose_name.replace("_", " ")
        object_label = cls.get_instance_label(instance)
        return f'{action.capitalize()} {object_name} "{object_label}"'

    @classmethod
    def build_state_change_message(cls, *, instance, action, before=None, after=None):
        before = before or {}
        after = after or {}

        if (
            instance._meta.label_lower == "preference.organisationdata"
            and before.get("organization_group") != after.get("organization_group")
        ):
            before_group_id = before.get("organization_group")
            after_group_id = after.get("organization_group")
            if action == "assigned" and after_group_id:
                group = OrganizationGroup.objects.filter(id=after_group_id).first()
                group_name = group.name if group else str(after_group_id)
                return f'Assigned organisation "{instance.name}" to organization group "{group_name}"'
            if action == "unassigned" and before_group_id:
                group = OrganizationGroup.objects.filter(id=before_group_id).first()
                group_name = group.name if group else str(before_group_id)
                return f'Unassigned organisation "{instance.name}" from organization group "{group_name}"'

        return cls.build_message(action, instance)

    @classmethod
    def _format_named_list(cls, names):
        if not names:
            return ""
        if len(names) == 1:
            return names[0]
        return ", ".join(names)

    @classmethod
    def _get_related_labels(cls, related_model, related_ids):
        if not related_model or not related_ids:
            return []
        queryset = related_model._default_manager.filter(id__in=related_ids)
        items_by_id = {item.id: cls.get_instance_label(item) for item in queryset}
        return [items_by_id[item_id] for item_id in related_ids if item_id in items_by_id]

    @classmethod
    def get_instance_label(cls, instance):
        if isinstance(instance, User):
            if instance.first_name:
                return instance.first_name
            if instance.email:
                return instance.email
            return str(instance.id)
        if isinstance(instance, UserInvitations):
            if instance.email:
                return instance.email
            if instance.phone_number:
                return instance.phone_number
            if instance.user_id:
                return str(instance.user_id)
            return str(instance.id)
        return str(instance)

    @classmethod
    def _build_access_code_workgroup_message(
        cls,
        instance,
        relation_name,
        action,
        related_model=None,
        related_ids=None,
    ):
        if instance._meta.label_lower == "preference.organisationaccesscode" and relation_name == "work_groups":
            work_group_names = cls._get_related_labels(related_model, related_ids)
            work_group_text = cls._format_named_list(work_group_names)
            if not work_group_text:
                return None
            verb = "Assigned" if action == "assigned" else "Unassigned"
            preposition = "to" if action == "assigned" else "from"
            suffix = "work group" if len(work_group_names) == 1 else "work groups"
            return f'{verb} access code "{instance.code}" {preposition} {work_group_text} {suffix}'

        if instance._meta.label_lower == "user_management.workgroup" and relation_name == "access_codes":
            access_code_labels = cls._get_related_labels(related_model, related_ids)
            access_code_text = cls._format_named_list(access_code_labels)
            if not access_code_text:
                return None
            verb = "Assigned" if action == "assigned" else "Unassigned"
            preposition = "to" if action == "assigned" else "from"
            code_label = "access code" if len(access_code_labels) == 1 else "access codes"
            return f'{verb} {code_label} "{access_code_text}" {preposition} {instance.name} work group'

        return None

    @classmethod
    def _build_user_organisation_message(
        cls,
        instance,
        relation_name,
        action,
        related_model=None,
        related_ids=None,
    ):
        if instance._meta.label_lower != "users.user" or relation_name != "organisation_data":
            return None

        organisation_names = cls._get_related_labels(related_model, related_ids)
        organisation_text = cls._format_named_list(organisation_names)
        if not organisation_text:
            return None

        verb = "Assigned" if action == "assigned" else "Unassigned"
        preposition = "to" if action == "assigned" else "from"
        suffix = "organisation" if len(organisation_names) == 1 else "organisations"
        return f'{verb} user "{cls.get_instance_label(instance)}" {preposition} {organisation_text} {suffix}'

    @classmethod
    def _build_user_workgroup_message(
        cls,
        instance,
        relation_name,
        action,
        related_model=None,
        related_ids=None,
    ):
        if instance._meta.label_lower != "users.user" or relation_name != "work_groups":
            return None

        work_group_names = cls._get_related_labels(related_model, related_ids)
        work_group_text = cls._format_named_list(work_group_names)
        if not work_group_text:
            return None

        verb = "Assigned" if action == "assigned" else "Unassigned"
        preposition = "to" if action == "assigned" else "from"
        suffix = "work group" if len(work_group_names) == 1 else "work groups"
        return f'{verb} user "{cls.get_instance_label(instance)}" {preposition} {work_group_text} {suffix}'

    @classmethod
    def build_m2m_message(
        cls,
        instance,
        relation_name,
        action,
        related_model=None,
        related_ids=None,
    ):
        custom_message = cls._build_access_code_workgroup_message(
            instance,
            relation_name,
            action,
            related_model=related_model,
            related_ids=related_ids,
        )
        if custom_message:
            return custom_message

        custom_message = cls._build_user_organisation_message(
            instance,
            relation_name,
            action,
            related_model=related_model,
            related_ids=related_ids,
        )
        if custom_message:
            return custom_message

        custom_message = cls._build_user_workgroup_message(
            instance,
            relation_name,
            action,
            related_model=related_model,
            related_ids=related_ids,
        )
        if custom_message:
            return custom_message

        object_name = instance._meta.verbose_name.replace("_", " ")
        object_label = cls.get_instance_label(instance)
        relation_label = relation_name.replace("_", " ")
        return f'{action.capitalize()} {relation_label} for {object_name} "{object_label}"'

    @classmethod
    def resolve_m2m_action(cls, instance, relation_name, operation):
        return cls.M2M_ACTION_RULES.get(
            (instance._meta.label_lower, relation_name, operation),
        )

    @classmethod
    def get_actor(cls, instance, action):
        if action == "password_reset" and isinstance(instance, User):
            return instance
        if instance._meta.label_lower == "user_management.organisationrolepermission":
            role = getattr(instance, "role", None)
            return getattr(role, "updated_by", None) or getattr(role, "created_by", None)
        if action == "created":
            return getattr(instance, "created_by", None)
        if action == "deleted":
            return getattr(instance, "deleted_by", None) or getattr(instance, "updated_by", None)
        return getattr(instance, "updated_by", None)

    @classmethod
    def resolve_organisation(cls, instance):
        if isinstance(instance, OrganisationData):
            return instance

        if instance._meta.label_lower == "user_management.organisationrolepermission":
            role = getattr(instance, "role", None)
            return getattr(role, "organisation", None)
        if instance._meta.label_lower == "users.userinvitations":
            return getattr(instance, "organisation", None)

        organisation = getattr(instance, "organisation", None)
        if organisation_id := getattr(instance, "organisation_id", None):
            return organisation or OrganisationData.objects.filter(id=organisation_id).first()

        if isinstance(instance, User):
            return instance.organisation_data.order_by("id").first()

        return None

    @classmethod
    def log_action(
        cls,
        *,
        instance,
        action,
        organisation=None,
        changes=None,
        message=None,
    ):
        payload_changes = changes or {"before": {}, "after": {}}
        if action in cls.ACTIONS_WITHOUT_CHANGES:
            payload_changes = {}

        activity_message = message or cls.build_message(action, instance)
        if not activity_message:
            return None
        # ignore logging when running migrations
        try:
            if cls.USER_ACTIVITY_TABLE not in connection.introspection.table_names():
                return None
        except Exception:
            return None

        actor_user = cls.get_actor(instance, action)
        actor_user = actor_user if getattr(actor_user, "is_authenticated", False) else None
        activity_organisation = organisation or cls.resolve_organisation(instance)

        try:
            return UserActivity.objects.create(
                actor=actor_user,
                action=action,
                record_type=cls.get_record_type(instance),
                record_id=str(instance.pk),
                organisation=activity_organisation,
                message=activity_message,
                changes=payload_changes,
            )
        except Exception:
            logger.exception(
                "Failed to log audit action=%s model=%s record_id=%s",
                action,
                instance._meta.label_lower,
                instance.pk,
            )
            return None
