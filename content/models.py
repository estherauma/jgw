from django.db import models
from django.utils import timezone

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
