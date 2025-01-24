from django.db import models
from django.utils import timezone

from preference.models import (
    Country,
    FactoryFarm,
    ImmigrationStatus,
    Language,
    Organisation,
    OrganisationData,
    OrganisationSector,
    Route,
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
