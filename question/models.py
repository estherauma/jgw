from django.db import models
from django.utils import timezone

from preference.models import (
    Country,
    FactoryFarm,
    Gender,
    ImmigrationStatus,
    Language,
    Organisation,
    OrganisationData,
    OrganisationSector,
    Route,
    OriginalSectorOfWork,
    SectorOfWork,
)


class InlineQuestionStandard(models.Model):
    data_source_id = models.CharField(max_length=24)
    device_id = models.CharField(max_length=255, blank=True, null=True)
    app_id = models.CharField(max_length=255, blank=True, null=True)
    locale = models.CharField(max_length=255, blank=True, null=True)

    route = models.ForeignKey(
        Route, on_delete=models.CASCADE, null=True, blank=True, related_name="inline_question_route"
    )
    preference = models.ForeignKey(
        "preference.Preference",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="inline_question_preference",
    )
    language = models.ForeignKey(
        Language, on_delete=models.CASCADE, null=True, blank=True, related_name="inline_question_language"
    )
    origin = models.ForeignKey(
        Country, on_delete=models.CASCADE, null=True, blank=True, related_name="inline_question_origin"
    )
    destination = models.ForeignKey(
        Country, on_delete=models.CASCADE, null=True, blank=True, related_name="inline_question_destination"
    )
    organisation_sector = models.ForeignKey(
        OrganisationSector,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="inline_question_organisation_sector",
    )
    factory_farm = models.ForeignKey(
        FactoryFarm,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="inline_question_factory_farm",
    )
    immigration_status = models.ForeignKey(
        ImmigrationStatus,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="inline_question_immigration_status",
    )
    organisation = models.ForeignKey(
        Organisation,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="inline_question_organisation",
    )
    org_code = models.CharField(max_length=255, blank=True, null=True)
    org_info = models.ForeignKey(OrganisationData, on_delete=models.SET_NULL, null=True, blank=True)
    org_work_code = models.CharField(max_length=255, blank=True, null=True)
    is_myvoice_organisation = models.BooleanField(default=False)
    api_version = models.CharField(max_length=10, blank=False, null=True)

    api_created_at = models.DateTimeField(default=timezone.now)
    api_updated_at = models.DateTimeField(default=timezone.now)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_org_info_cleaned = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.id}"


class InlineQuestionText(models.Model):
    text = models.TextField(blank=True, null=True)
    title_text = models.TextField(blank=True, null=True)
    translated_text = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return f"{self.text}"


class InlineQuestion(models.Model):
    question = models.ForeignKey(InlineQuestionText, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    inline_question_standard = models.ForeignKey(
        InlineQuestionStandard, on_delete=models.CASCADE, related_name="question_standard"
    )

    def __str__(self) -> str:
        return f"{self.question}"


class InlineQuestionResponseText(models.Model):
    translated_text = models.TextField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return f"{self.translated_text}"


class InlineQuestionResponse(models.Model):
    inline_question = models.ForeignKey(InlineQuestion, on_delete=models.CASCADE)
    response = models.ForeignKey(InlineQuestionResponseText, on_delete=models.CASCADE, null=True, blank=True)
    organisation_inline_question = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return f"{self.inline_question.question.text} -> {self.response.translated_text}"


class InlineQuestionAndKeysMatch(models.Model):
    inline_question = models.TextField(max_length=255)
    inline_question_key = models.TextField(max_length=255, null=True)
    custom_lang = models.CharField(max_length=5, null=True, blank=True)

    def __str__(self) -> str:
        return f"{self.inline_question} -> {self.inline_question_key}"


class FollowUpQuestion(models.Model):
    inline_question = models.ForeignKey(
        InlineQuestionAndKeysMatch, on_delete=models.CASCADE, related_name="inline_question_follow_question"
    )
    followup_question = models.TextField(max_length=255)
    followup_question_key = models.TextField(max_length=255, null=True)
    custom_lang = models.CharField(max_length=5, null=True, blank=True)


class MessagingQuestionStandard(models.Model):
    data_source_id = models.CharField(max_length=24)
    device_id = models.CharField(max_length=255, blank=True, null=True)
    app_id = models.CharField(max_length=255, blank=True, null=True)
    question_id = models.CharField(max_length=255, blank=True, null=True)
    message_id = models.CharField(max_length=255, blank=True, null=True)
    locale = models.CharField(max_length=255, blank=True, null=True)

    route = models.ForeignKey(
        Route, on_delete=models.CASCADE, null=True, blank=True, related_name="messaging_question_route"
    )
    preference = models.ForeignKey(
        "preference.Preference",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="messaging_question_preference",
    )
    origin = models.ForeignKey(
        Country, on_delete=models.CASCADE, null=True, blank=True, related_name="messaging_question_origin"
    )
    destination = models.ForeignKey(
        Country,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="messaging_question_destination",
    )
    immigration_status = models.ForeignKey(
        ImmigrationStatus,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="messaging_question_immigration_status",
    )
    sectors_of_work = models.ManyToManyField(
        OriginalSectorOfWork,
        related_name="messaging_question_sectors_of_work",
    )
    organisation_sector = models.ForeignKey(
        OrganisationSector,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="messaging_question_organisation_sector",
    )
    factory_farm = models.ForeignKey(
        FactoryFarm,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="messaging_question_factory_farm",
    )
    organisation = models.ForeignKey(
        Organisation,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="messaging_question_organisation",
    )
    org_code = models.CharField(max_length=255, blank=True, null=True)
    org_info = models.ForeignKey(OrganisationData, on_delete=models.SET_NULL, null=True, blank=True)
    language = models.ForeignKey(
        Language, on_delete=models.CASCADE, null=True, blank=True, related_name="messaging_question_language"
    )
    question_version = models.CharField(max_length=255, blank=True, null=True)
    is_myvoice_organisation = models.BooleanField(default=False)
    is_org_info_cleaned = models.BooleanField(default=False)
    api_created_at = models.DateTimeField(default=timezone.now)
    api_updated_at = models.DateTimeField(default=timezone.now)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.id}"


class MessagingQuestionText(models.Model):
    text = models.CharField(max_length=255, blank=True, null=True, unique=True)
    translated_text = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return f"{self.translated_text}"


class MessagingQuestion(models.Model):
    question = models.ForeignKey(MessagingQuestionText, on_delete=models.CASCADE, null=True, blank=True)
    messaging_question_standard = models.ForeignKey(
        MessagingQuestionStandard, on_delete=models.CASCADE, related_name="question_standard"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.question.translated_text}"


class MessagingResponseOptionText(models.Model):
    option = models.TextField(blank=True, null=True)
    translated_option = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return f"{self.translated_option}"


class MessagingResponse(models.Model):
    option = models.ForeignKey(MessagingResponseOptionText, on_delete=models.CASCADE, null=True, blank=True)
    value = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.option.translated_option}"


class MessagingQuestionResponse(models.Model):
    messaging_question = models.ForeignKey(MessagingQuestion, on_delete=models.CASCADE)
    responses = models.ManyToManyField(MessagingResponse)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class QuestionCategory(models.Model):
    name = models.CharField(max_length=255)
    code = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name}"


class InlineQuestionV1(models.Model):
    """
    Stores inline question data (page_id, page_title, question_key, question_text, question_category).
    This table normalizes question data so it can be referenced by Lead, Followup, and FollowupFollowup tables.
    """
    page_id = models.CharField(max_length=255)
    page_title = models.TextField(blank=True, null=True)
    question_key = models.TextField(blank=True, null=True, db_index=True)
    question_text = models.TextField(blank=True, null=True)
    question_category = models.ForeignKey(
        QuestionCategory, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name="inline_questions_v1"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=["question_key"]),
            models.Index(fields=["question_text"]),
        ]

    def __str__(self):
        return f"{self.question_key or self.question_text}"


class InlineQuestionResponseV1(models.Model):
    """
    Stores inline question response data (response_key, response_text, response_text_translated).
    This table normalizes response data so it can be referenced by Lead, Followup, and FollowupFollowup tables.
    """
    response_key = models.TextField(blank=True, null=True, db_index=True)
    response_text = models.TextField(blank=True, null=True)
    response_text_translated = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=["response_key"]),
            models.Index(fields=["response_text"]),
        ]

    def __str__(self):
        return f"{self.response_key or self.response_text}"


class MessagingQuestionV1(models.Model):
    """
    Stores messaging question data (question_key, question_text, question_category).
    This table normalizes question data so it can be referenced by Lead, Followup, and FollowupFollowup tables.
    """
    page_id = models.CharField(max_length=255)
    page_title = models.TextField(blank=True, null=True)
    question_key = models.TextField(blank=True, null=True, db_index=True)
    question_text = models.TextField(blank=True, null=True)
    question_category = models.ForeignKey(
        QuestionCategory, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name="messaging_questions_v1"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=["question_key"]),
            models.Index(fields=["question_text"]),
        ]

    def __str__(self):
        return f"{self.question_key or self.question_text}"


class MessagingQuestionResponseV1(models.Model):
    """
    Stores messaging question response data (response_key, response_text, response_text_translated).
    This table normalizes response data so it can be referenced by Lead, Followup, and FollowupFollowup tables.
    """
    response_key = models.TextField(blank=True, null=True, db_index=True)
    response_text = models.TextField(blank=True, null=True)
    response_text_translated = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=["response_key"]),
            models.Index(fields=["response_text"]),
        ]

    def __str__(self):
        return f"{self.response_key or self.response_text}"


class LeadMessagingQuestionResponse(models.Model):
    """
    Lead/initial messaging question response.
    Contains all metadata and references to MessagingQuestionV1 and MessagingQuestionResponseV1.
    """
    data_source_id = models.CharField(max_length=24)
    device_id = models.CharField(max_length=255)
    app_id = models.CharField(max_length=255, blank=True, null=True)

    messaging_question = models.ForeignKey(
        MessagingQuestionV1,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="lead_responses"
    )
    
    messaging_question_response = models.ForeignKey(
        MessagingQuestionResponseV1,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="lead_responses"
    )
    
    response_value = models.TextField(blank=True, null=True)
    
    route = models.ForeignKey(
        Route, on_delete=models.CASCADE, null=True, blank=True, related_name="lead_messaging_question_route"
    )
    preference = models.ForeignKey(
        "preference.Preference",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="lead_messaging_question_preference",
    )
    origin = models.ForeignKey(
        Country, on_delete=models.CASCADE, null=True, blank=True, related_name="lead_messaging_question_origin"
    )
    destination = models.ForeignKey(
        Country,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="lead_messaging_question_destination",
    )
    immigration_status = models.ForeignKey(
        ImmigrationStatus,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="lead_messaging_question_immigration_status",
    )
    organisation_sector = models.ForeignKey(
        OrganisationSector,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="lead_messaging_question_organisation_sector",
    )
    org_info = models.ForeignKey(OrganisationData, on_delete=models.SET_NULL, null=True, blank=True)
    language = models.ForeignKey(
        Language, on_delete=models.CASCADE, null=True, blank=True, related_name="lead_messaging_question_language"
    )
    locale = models.ForeignKey(Country, on_delete=models.SET_NULL, null=True, blank=True, related_name="lead_messaging_question_locale")
    
    question_response_date = models.DateTimeField(blank=True, null=True)
    api_created_at = models.DateTimeField(default=timezone.now)
    api_updated_at = models.DateTimeField(default=timezone.now)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=["data_source_id"]),
            models.Index(fields=["device_id"]),
            models.Index(fields=["api_created_at"]),
        ]

    def __str__(self):
        question_text = self.messaging_question.question_text if self.messaging_question else "No question"
        return f"{question_text} - {self.device_id}"


class FollowupMessagingQuestionResponse(models.Model):
    """
    Follow-up messaging question response.
    References the lead question and MessagingQuestionV1/MessagingQuestionResponseV1.
    """
    lead_question = models.ForeignKey(
        LeadMessagingQuestionResponse,
        on_delete=models.CASCADE,
        related_name='followup_responses'
    )
    data_source_id = models.CharField(max_length=24)
    device_id = models.CharField(max_length=255)

    messaging_question = models.ForeignKey(
        MessagingQuestionV1,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="followup_responses"
    )
    
    messaging_question_response = models.ForeignKey(
        MessagingQuestionResponseV1,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="followup_responses"
    )
    
    # Keep response_value for backward compatibility or additional data
    response_value = models.TextField(blank=True, null=True)
    
    question_response_date = models.DateTimeField(blank=True, null=True)
    api_created_at = models.DateTimeField(default=timezone.now)
    api_updated_at = models.DateTimeField(default=timezone.now)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=["lead_question"]),
            models.Index(fields=["data_source_id"]),
            models.Index(fields=["device_id"]),
        ]

    def __str__(self):
        question_text = self.messaging_question.question_text if self.messaging_question else "No question"
        return f"{question_text} - {self.device_id}"


class FollowupFollowupMessagingQuestionResponse(models.Model):
    """
    Follow-up of follow-up messaging question response.
    References the followup question and MessagingQuestionV1/MessagingQuestionResponseV1.
    """
    followup_question = models.ForeignKey(
        FollowupMessagingQuestionResponse,
        on_delete=models.CASCADE,
        related_name='followup_followup_responses'
    )
    data_source_id = models.CharField(max_length=24)
    device_id = models.CharField(max_length=255)
    
    # Reference to normalized question data
    messaging_question = models.ForeignKey(
        MessagingQuestionV1,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="followup_followup_responses"
    )
    
    # Reference to normalized response data
    messaging_question_response = models.ForeignKey(
        MessagingQuestionResponseV1,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="followup_followup_responses"
    )
    
    response_value = models.TextField(blank=True, null=True)
    
    question_response_date = models.DateTimeField(blank=True, null=True)
    api_created_at = models.DateTimeField(default=timezone.now)
    api_updated_at = models.DateTimeField(default=timezone.now)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=["followup_question"]),
            models.Index(fields=["data_source_id"]),
            models.Index(fields=["device_id"]),
        ]

    def __str__(self):
        question_text = self.messaging_question.question_text if self.messaging_question else "No question"
        return f"{question_text} - {self.device_id}"


class ActualMessageSent(models.Model):
    message_id = models.CharField(max_length=255)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'actual_message_sent'
        verbose_name = 'Actual Message Sent'
        verbose_name_plural = 'Actual Messages Sent'

    def __str__(self):
        return f"{self.message_id}"
    
class MessageDataSent(models.Model):
    message_id = models.CharField(max_length=255)
    message_content = models.ForeignKey(ActualMessageSent, on_delete=models.SET_NULL, null=True, related_name='actual_message_data')
    message_title = models.TextField()
    message_title_english = models.TextField()
    message_date = models.DateTimeField()
    message_delivered_date = models.DateField(null=True)
    message_notification_response_code = models.CharField(max_length=255, blank=True)
    message_notification_response_message = models.TextField(blank=True)

    message_queued = models.BooleanField(default=False)
    message_delivered = models.BooleanField(default=False)
    message_notification_sent_to_fcm = models.BooleanField(default=False)

    device_id = models.CharField(max_length=255)
    device_model = models.CharField(max_length=255)
    app_id = models.CharField(max_length=255)
    app_version = models.CharField(max_length=255)
    registration_token = models.TextField(blank=True)

    language = models.ForeignKey(Language, on_delete=models.SET_NULL, null=True, related_name="message_data")
    destination = models.ForeignKey(
        Country, on_delete=models.SET_NULL, null=True, related_name="destination_messages"
    )
    origin_country = models.ForeignKey(
        Country, on_delete=models.SET_NULL, null=True, related_name="origin_messages"
    )
    organisation = models.ForeignKey(
        Organisation, on_delete=models.SET_NULL, null=True, related_name="message_data"
    )

    destination_state = models.CharField(max_length=255, blank=True)
    immigration_status = models.CharField(max_length=255, blank=True)
    age = models.CharField(max_length=255)
    gender = models.ForeignKey(Gender, on_delete=models.SET_NULL, null=True, blank=True)
    seen_tab_welcome_text = models.CharField(max_length=255)
    factory_farm = models.CharField(max_length=255, blank=True)

    user_created_at = models.DateTimeField()
    user_updated_at = models.DateTimeField()
    api_created_at = models.DateTimeField(auto_now_add=True)
    api_updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=["message_id"]),
            models.Index(fields=["device_id"]),
            models.Index(fields=["message_date"]),
        ]

    def __str__(self):
        return f"{self.message_id} - {self.device_id}"


class LeadInlineQuestionResponse(models.Model):
    """
    Lead/initial inline question response.
    Contains all metadata and references to InlineQuestionV1 and InlineQuestionResponseV1.
    """
    data_source_id = models.CharField(max_length=24)  
    device_id = models.CharField(max_length=255)
    app_id = models.CharField(max_length=255, blank=True, null=True)

    inline_question = models.ForeignKey(
        InlineQuestionV1,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="lead_inline_responses"
    )
    
    # Reference to normalized response data
    inline_question_response = models.ForeignKey(
        InlineQuestionResponseV1,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="lead_inline_responses"
    )
    
    # Keep response_value for backward compatibility or additional data
    response_value = models.TextField(blank=True, null=True)
    
    organisation = models.ForeignKey(
        OrganisationData, 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True,
        related_name='lead_question_organisation'
    )
    organisation_code = models.CharField(max_length=255, blank=True, null=True)
    language = models.ForeignKey(
        Language, 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True,
        related_name='lead_question_language'
    )
    destination = models.ForeignKey(
        Country, 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True,
        related_name='lead_question_destination'
    )
    immigration_status = models.ForeignKey(
        ImmigrationStatus, 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True,
        related_name='lead_question_immigration_status'
    )
    factory_farm = models.ForeignKey(
        FactoryFarm, 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True,
        related_name='lead_question_factory_farm'
    )
    locale = models.ForeignKey(
        Country, 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True,
        related_name='lead_question_locale'
    )
    question_response_date = models.DateTimeField()
    api_created_at = models.DateTimeField()
    api_updated_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=["data_source_id"]),
            models.Index(fields=["device_id"]),
            models.Index(fields=["api_created_at"]),
        ]

    def __str__(self):
        question_text = self.inline_question.question_text if self.inline_question else "No question"
        return f"{question_text} - {self.device_id}"

class FollowupInlineQuestionResponse(models.Model):
    """
    Follow-up inline question response.
    References the lead question and InlineQuestionV1/InlineQuestionResponseV1.
    """
    lead_question = models.ForeignKey(
        LeadInlineQuestionResponse, 
        on_delete=models.CASCADE,
        related_name='followup_responses'
    )
    data_source_id = models.CharField(max_length=24)
    device_id = models.CharField(max_length=255)

    inline_question = models.ForeignKey(
        InlineQuestionV1,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="followup_inline_responses"
    )
    
    inline_question_response = models.ForeignKey(
        InlineQuestionResponseV1,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="followup_inline_responses"
    )
    
    response_value = models.TextField(blank=True, null=True)
    
    question_response_date = models.DateTimeField()
    api_created_at = models.DateTimeField()
    api_updated_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=["lead_question"]),
            models.Index(fields=["data_source_id"]),
            models.Index(fields=["device_id"]),
        ]

    def __str__(self):
        question_text = self.inline_question.question_text if self.inline_question else "No question"
        return f"{question_text} - {self.device_id}"

class FollowupFollowupInlineQuestionResponse(models.Model):
    """
    Follow-up of follow-up inline question response.
    References the followup question and InlineQuestionV1/InlineQuestionResponseV1.
    """
    followup_question = models.ForeignKey(
        FollowupInlineQuestionResponse,
        on_delete=models.CASCADE,
        related_name='followup_followup_responses'
    )
    data_source_id = models.CharField(max_length=24)
    device_id = models.CharField(max_length=255)
    
    inline_question = models.ForeignKey(
        InlineQuestionV1,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="followup_followup_inline_responses"
    )
    
    inline_question_response = models.ForeignKey(
        InlineQuestionResponseV1,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="followup_followup_inline_responses"
    )
    
    response_value = models.TextField(blank=True, null=True)
    
    question_response_date = models.DateTimeField()
    api_created_at = models.DateTimeField()
    api_updated_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=["followup_question"]),
            models.Index(fields=["data_source_id"]),
            models.Index(fields=["device_id"]),
        ]

    def __str__(self):
        question_text = self.inline_question.question_text if self.inline_question else "No question"
        return f"{question_text} - {self.device_id}"


