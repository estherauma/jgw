from django.db import models
from django.conf import settings
from django.utils import timezone

from common.current_user import get_current_user

class SoftDeleteManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_deleted=False)

class AuditFieldsMixin(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, 
        null=True, blank=True, related_name="%(app_label)s_%(class)s_created"
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name="%(app_label)s_%(class)s_updated"
    )
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)
    deleted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        null=True, blank=True, on_delete=models.SET_NULL,
        related_name="%(app_label)s_%(class)s_deleted"
    )
    objects = SoftDeleteManager()
    all_objects = models.Manager() 
    
    class Meta:
        abstract = True
        base_manager_name = "all_objects"

    def save(self, *args, **kwargs):
        current_user = get_current_user()
        auto_update_fields = set()
        is_adding = self._state.adding

        if getattr(current_user, "is_authenticated", False):
            if is_adding and not self.created_by_id:
                self.created_by = current_user
                auto_update_fields.add("created_by")

            if not (self.is_deleted and self.deleted_by_id) and self.updated_by_id != current_user.id:
                self.updated_by = current_user
                auto_update_fields.add("updated_by")

        update_fields = kwargs.get("update_fields")
        if update_fields is not None and auto_update_fields:
            kwargs["update_fields"] = set(update_fields) | auto_update_fields

        return super().save(*args, **kwargs)
        
    def soft_delete(self, deleted_by):
        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.deleted_by = deleted_by
        self.updated_by = deleted_by
        self.save()
