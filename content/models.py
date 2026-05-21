from django.db import models
from django.utils import timezone
from common.models import AuditFieldsMixin

class AggregatedContent(models.Model):
    """
    Stores aggregated content from Strapi for translation processing
    """
    content = models.JSONField(help_text="The aggregated content from Strapi in JSON format")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Pending'),
            ('completed', 'Completed'),
            ('failed', 'Failed')
        ],
        default='pending'
    )

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Aggregated Content'
        verbose_name_plural = 'Aggregated Contents'

    def __str__(self):
        return f"Aggregated Content {self.id} - {self.status}"


class Locale(AuditFieldsMixin):
    name = models.CharField(max_length=255)
    code = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name

    class Meta(AuditFieldsMixin.Meta):
        pass


class WorkSector(AuditFieldsMixin):
    slug = models.CharField(max_length=255, unique=True)
    display_name = models.CharField(max_length=255)

    def __str__(self):
        return self.display_name

    class Meta(AuditFieldsMixin.Meta):
        pass


class Collection(AuditFieldsMixin):
    name = models.CharField(max_length=255)
    api_name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name

    class Meta(AuditFieldsMixin.Meta):
        pass
