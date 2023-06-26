from django.db import models

class InlineQuestionStandard(models.Model):
    data_source_id = models.CharField(max_length=24)
    device_id = models.CharField(max_length=255)
    app_id = models.CharField(max_length=255)
    locale = models.CharField(max_length=255, blank=True, null=True)
    route = models.CharField(max_length=255, blank=True, null=True)
    language = models.CharField(max_length=255, blank=True, null=True)
    organisation = models.CharField(max_length=255, blank=True, null=True)
    organisation_sector = models.CharField(max_length=255, blank=True, null=True)
    factory_farm = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()
    
    def __str__(self):
        return f"InlineQuestion {self.id}"


class InlineQuestion(models.Model):
    question = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self) -> str:
        return f"InlineQuestion {self.question}"
    

class InlineQuestionResponse(models.Model):
    inline_question_standard = models.ForeignKey(InlineQuestionStandard, on_delete=models.CASCADE)
    inline_question = models.ForeignKey(InlineQuestion, on_delete=models.CASCADE)
    response = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self) -> str:
        return f"InlineQuestionResponse {self.response}"
    