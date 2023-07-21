from django.db import models

from preference.models import Country, FactoryFarm, Language, Organisation, OrganisationSector, Route

class InlineQuestionStandard(models.Model):
    data_source_id = models.CharField(max_length=24)
    device_id = models.CharField(max_length=255)
    app_id = models.CharField(max_length=255)
    locale = models.CharField(max_length=255, blank=True, null=True)
    
    
    route = models.ForeignKey(Route, on_delete=models.SET_NULL, null=True, blank=True, related_name='inline_question_route')
    preference = models.ForeignKey('preference.Preference', on_delete=models.SET_NULL, null=True, blank=True, related_name='inline_question_preference')
    language = models.ForeignKey(Language, on_delete=models.SET_NULL, null=True, blank=True, related_name='inline_question_language')
    origin = models.ForeignKey(Country, on_delete=models.SET_NULL, null=True, blank=True, related_name='inline_question_origin')
    destination = models.ForeignKey(Country, on_delete=models.SET_NULL, null=True, blank=True, related_name='inline_question_destination')
    organisation_sector = models.ForeignKey(OrganisationSector, on_delete=models.SET_NULL, null=True, blank=True, related_name='inline_question_organisation_sector')
    factory_farm = models.ForeignKey(FactoryFarm, on_delete=models.SET_NULL, null=True, blank=True, related_name='inline_question_factory_farm')
    organisation = models.ForeignKey(Organisation, on_delete=models.SET_NULL, null=True, blank=True, related_name='inline_question_organisation')
    
    
    api_created_at = models.DateTimeField()
    api_updated_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"InlineQuestion {self.id}"



class InlineQuestionText(models.Model):
    text = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self) -> str:
        return f"InlineQuestionText {self.text}"



class InlineQuestion(models.Model):
    question = models.ForeignKey(InlineQuestionText, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    inline_question_standard = models.ForeignKey(InlineQuestionStandard, on_delete=models.CASCADE)
    
    def __str__(self) -> str:
        return f"InlineQuestion {self.question}"



class InlineQuestionResponse(models.Model):
    inline_question = models.ForeignKey(InlineQuestion, on_delete=models.CASCADE)
    response = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self) -> str:
        return f"InlineQuestionResponse {self.response}"
    
    

class MessagingQuestionStandard(models.Model):
    data_source_id = models.CharField(max_length=24)
    device_id = models.CharField(max_length=255)
    app_id = models.CharField(max_length=255)
    question_id = models.CharField(max_length=255, blank=True, null=True)
    message_id = models.CharField(max_length=255, blank=True, null=True)
    locale = models.CharField(max_length=255, blank=True, null=True)
    
    route = models.ForeignKey(Route, on_delete=models.SET_NULL, null=True, blank=True, related_name='messaging_question_route')
    preference = models.ForeignKey('preference.Preference', on_delete=models.SET_NULL, null=True, blank=True, related_name='messaging_question_preference')
    origin = models.ForeignKey(Country, on_delete=models.SET_NULL, null=True, blank=True, related_name='messaging_question_origin')
    destination = models.ForeignKey(Country, on_delete=models.SET_NULL, null=True, blank=True, related_name='messaging_question_destination')
    
    api_created_at = models.DateTimeField()
    api_updated_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    
    def __str__(self):
        return f"MessagingQuestion {self.id}"
    
    
class MessagingQuestion(models.Model):
    question = models.CharField(max_length=255, blank=True, null=True)
    messaging_question_standard = models.ForeignKey(MessagingQuestionStandard, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"MessagingQuestion {self.question}"
    

MESAGING_QUESTION_RESPONSE_OPTION_TYPE_CHOICES = (
    ('text', 'Text'),
    ('multiple', 'Multiple'),
)

class MessagingQuestionResponse(models.Model):
    messaging_question = models.ForeignKey(MessagingQuestion, on_delete=models.CASCADE)
    response_text = models.CharField(max_length=255, blank=True, null=True)
    response_option_type = models.CharField(
        max_length=255,
        choices=MESAGING_QUESTION_RESPONSE_OPTION_TYPE_CHOICES,
        blank=True,
        null=True,
        default="text"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"MessagingQuestionResponse {self.response_text}"
    
class MessagingQuestionOptionResponseAnswer(models.Model):
    messaging_question_response = models.ForeignKey(MessagingQuestionResponse, on_delete=models.CASCADE)
    option = models.CharField(max_length=255, blank=True, null=True)
    answer = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"MessagingQuestionResponseOption {self.option}"