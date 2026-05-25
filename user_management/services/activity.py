import logging
from datetime import date, datetime
from decimal import Decimal

from django.db import models
from user_management.models import UserActivity

logger = logging.getLogger(__name__)


class UserActivityService:
    ORGANISATION_RECORD_TYPE = "organisation"

    @classmethod
    def _normalize(cls, value):
        if isinstance(value, models.Model):
            return value.pk
        if hasattr(value, "all") and callable(getattr(value, "all")):
            return [cls._normalize(item) for item in value.all()]
        if isinstance(value, (datetime, date)):
            return value.isoformat()
        if isinstance(value, Decimal):
            return str(value)
        if isinstance(value, dict):
            return {str(key): cls._normalize(item) for key, item in value.items()}
        if isinstance(value, (list, tuple, set)):
            return [cls._normalize(item) for item in value]
        return value

    @classmethod
    def organisation_state(cls, organisation):
        if not organisation:
            return {}
            
        access_code = (
            organisation.organisation_access_codes.order_by("created_at", "id")
            .values_list("code", flat=True)
            .first()
        )
        collection_languages = list(
            organisation.collection_languages.order_by("code").values_list("code", flat=True)
        )
        
        data = {
            "name": organisation.name,
            "org_code": organisation.org_code,
            "display_name": organisation.display_name,
            "has_custom_content": organisation.has_custom_content,
            "content_collection": organisation.content_collection,
            "default_collection_language": organisation.default_collection_language,
            "work_sector": organisation.work_sector,
            "custom_type": organisation.custom_type,
            "theme": organisation.theme,
            "default_report_issue_emails": organisation.default_report_issue_emails,
            "default_feedback_emails": organisation.default_feedback_emails,
            "organization_group_id": organisation.organization_group_id,
            "access_code": access_code,
            "collection_languages": collection_languages,
        }
        return {key: cls._normalize(value) for key, value in data.items()}

    @classmethod
    def build_changes(cls, before=None, after=None):
        before = before or {}
        after = after or {}
        changed_before = {}
        changed_after = {}

        for key in sorted(set(before.keys()) | set(after.keys())):
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
    def log_action(
        cls,
        *,
        actor,
        action,
        record_type,
        record_id,
        organisation=None,
        message,
        changes=None,
    ):
        if not message:
            return None

        actor_user = actor if getattr(actor, "is_authenticated", False) else None
        payload_changes = changes or {"before": {}, "after": {}}
        
        if "before" not in payload_changes or "after" not in payload_changes:
            payload_changes = {
                "before": payload_changes.get("before", {}),
                "after": payload_changes.get("after", {}),
            }

        try:
            return UserActivity.objects.create(
                actor=actor_user,
                action=action,
                record_type=record_type,
                record_id=str(record_id),
                organisation=organisation,
                message=message,
                changes=payload_changes,
            )
        except Exception:
            logger.exception(
                "Failed to log user activity action=%s record_type=%s record_id=%s",
                action,
                record_type,
                record_id,
            )
            return None

    @classmethod
    def log_organisation_created(cls, *, actor, organisation, after_state=None):
        after_state = after_state or cls.organisation_state(organisation)
        return cls.log_action(
            actor=actor,
            action=UserActivity.Action.CREATED,
            record_type=cls.ORGANISATION_RECORD_TYPE,
            record_id=organisation.id,
            organisation=organisation,
            message=f'Created organisation "{organisation.name}"',
            changes={"before": {}, "after": after_state},
        )

    @classmethod
    def log_organisation_updated(cls, *, actor, organisation, before_state=None, after_state=None):
        changes = cls.build_changes(before_state, after_state)
        # Cleaned up: Removed heavy snapshot fallback if no changes occurred.
        return cls.log_action(
            actor=actor,
            action=UserActivity.Action.UPDATED,
            record_type=cls.ORGANISATION_RECORD_TYPE,
            record_id=organisation.id,
            organisation=organisation,
            message=f'Updated organisation "{organisation.name}"',
            changes=changes,
        )

    @classmethod
    def log_organisation_deleted(
        cls,
        *,
        actor,
        organisation_id,
        organisation_name,
        organisation=None,
        before_state=None,
    ):
        return cls.log_action(
            actor=actor,
            action=UserActivity.Action.DELETED,
            record_type=cls.ORGANISATION_RECORD_TYPE,
            record_id=organisation_id,
            organisation=organisation,
            message=f'Deleted organisation "{organisation_name}"',
            changes={"before": before_state or {}, "after": {}},
        )