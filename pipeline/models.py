from django.db import models

class CommandLog(models.Model):
    command_name = models.CharField(max_length=255)
    data_fetch = models.TextField(null=True, blank=True)
    command_status = models.BooleanField()
    error = models.TextField(null=True, blank=True)
    executed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.command_name} - {self.executed_at} - {'Success' if self.command_status else 'Failure'}"
