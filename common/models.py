from django.db import models
from django.conf import settings
from django.utils import timezone

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
        
    def soft_delete(self, deleted_by):
        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.is_active = False
        self.deleted_by = deleted_by
        self.updated_by = deleted_by
        self.save()