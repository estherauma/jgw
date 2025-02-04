from django.db import models
from django.db.models import Index


from django.db import models

from preference.models import (
    Age,
    Country,
    CountryState,
    FactoryFarm,
    Gender,
    ImmigrationStatus,
    Language,
    Organisation,
    OrganisationSector,
    Preference,
    Route,
    SectorOfWork,
)


class TimestampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class BigQueryChaptersData(TimestampedModel):
    event_date = models.DateField()
    chapters = models.CharField(max_length=50)
    users = models.IntegerField(default=0)
    count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.chapters


class BigQueryFirstOpenHomepageData(TimestampedModel):
    """
    This model is used to store data from BigQueryFirstOpenHomepageData
    event_name are :  homepage, first_open
    """

    event_date = models.DateField()
    users = models.IntegerField(default=0)
    count = models.IntegerField(default=0)
    event_name = models.CharField(max_length=100, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.event_name


class OneTimeEventJob(TimestampedModel):
    name = models.CharField(max_length=255)
    run = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class Chapter(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    number_key = models.CharField(max_length=100)
    chapter_text = models.CharField(max_length=255, null=True, blank=True)
    destination = models.ForeignKey(
        Country,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="chapter_tittle_opened_destination",
    )

    def __str__(self):
        return self.number_key


class ChaptersOpened(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    event_created_at = models.DateTimeField(null=True, blank=True)
    event_updated_at = models.DateTimeField(null=True, blank=True)
    event_name = models.CharField(max_length=255)
    chapter = models.ForeignKey(
        Chapter, null=True, blank=True, on_delete=models.SET_NULL, related_name="chapter_opened_chapters"
    )
    organisation = models.ForeignKey(Organisation, on_delete=models.SET_NULL, null=True, blank=True)
    age = models.ForeignKey(Age, on_delete=models.SET_NULL, null=True, blank=True)
    language = models.ForeignKey(Language, on_delete=models.SET_NULL, null=True, blank=True)
    gender = models.ForeignKey(Gender, on_delete=models.SET_NULL, null=True, blank=True)
    organisation_sector = models.ForeignKey(
        OrganisationSector, on_delete=models.SET_NULL, null=True, blank=True
    )
    device_id = models.CharField(max_length=255, null=True, blank=True)
    app_id = models.CharField(max_length=255, null=True, blank=True)
    destination_state = models.ForeignKey(
        CountryState,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="chapters_opened_destination_state",
    )
    destination = models.ForeignKey(
        Country, on_delete=models.SET_NULL, null=True, blank=True, related_name="chapters_opened_destination"
    )
    immigration_status = models.ForeignKey(
        ImmigrationStatus, on_delete=models.SET_NULL, null=True, blank=True
    )

    preference = models.ForeignKey(
        Preference,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="chapters_opened_preference",
    )
    factory_farm = models.ForeignKey(
        FactoryFarm,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="chapters_opened_factory_farm",
    )
    origin = models.ForeignKey(
        Country, on_delete=models.SET_NULL, null=True, blank=True, related_name="chapters_opened_origin"
    )
    is_myvoice_organisation = models.BooleanField(default=False)

    def __str__(self):
        return f"ChaptersOpened {self.event_name}"

    class Meta:
        indexes = [
            Index(fields=["event_name"]),
            Index(fields=["chapter"]),
            Index(fields=["device_id"]),
            Index(fields=["destination"]),
        ]


class ChaptersFeedbackStandard(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    api_created_at = models.DateTimeField(null=True, blank=True)
    api_updated_at = models.DateTimeField(null=True, blank=True)
    data_source_id = models.CharField(max_length=255, null=True, blank=True)
    device_id = models.CharField(max_length=255, null=True, blank=True)
    locale = models.CharField(max_length=255, null=True, blank=True)
    preference = models.ForeignKey(
        "preference.Preference",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="chapter_feedback_preference",
    )
    feedback_title = models.CharField(null=True, blank=True, max_length=255)
    gender = models.ForeignKey(Gender, on_delete=models.SET_NULL, null=True, blank=True)
    age = models.ForeignKey(Age, on_delete=models.SET_NULL, null=True, blank=True)
    language = models.ForeignKey(Language, on_delete=models.SET_NULL, null=True, blank=True)
    origin = models.ForeignKey(
        Country, on_delete=models.SET_NULL, null=True, blank=True, related_name="chapter_feedback_origin"
    )
    destination = models.ForeignKey(
        Country, on_delete=models.SET_NULL, null=True, blank=True, related_name="chapter_feedback_destination"
    )
    destination_state = models.ForeignKey(
        Country,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="chapter_feedback_destination_state",
    )
    immigration_status = models.ForeignKey(
        ImmigrationStatus, on_delete=models.SET_NULL, null=True, blank=True
    )
    route = models.ForeignKey(Route, on_delete=models.SET_NULL, null=True, blank=True)
    organisation_sector = models.ForeignKey(
        OrganisationSector, on_delete=models.SET_NULL, null=True, blank=True
    )
    factory_farm = models.ForeignKey(FactoryFarm, on_delete=models.SET_NULL, null=True, blank=True)
    organisation = models.ForeignKey(Organisation, on_delete=models.SET_NULL, null=True, blank=True)
    sectors_of_work = models.ManyToManyField(SectorOfWork)
    is_myvoice_organisation = models.BooleanField(default=False)

    def __str__(self):
        return self.data_source_id


class ChaptersFeedbackResponse(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    response = models.TextField()
    translated_response = models.TextField(null=True, blank=True)
    # TODO: add relationship chapter

    def __str__(self):
        return self.response


class ChaptersFeedbackQuestion(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    question = models.TextField()
    transalted_question = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.question


class ChaptersFeedback(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    feedback_standard = models.ForeignKey(
        ChaptersFeedbackStandard,
        on_delete=models.CASCADE,
        null=True,
        related_name="chapterfeedback_feedback_standards",
    )
    feedback_question = models.ForeignKey(
        ChaptersFeedbackQuestion,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="chapterfeedback_feedback_questions",
    )
    feedback_response = models.ForeignKey(
        ChaptersFeedbackResponse,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="chapterfeedback_feedback_responses",
    )
    chapter = models.ForeignKey(
        Chapter, on_delete=models.SET_NULL, null=True, blank=False, related_name="chapterfeedback_chapters"
    )

    def __str__(self):
        return self.feedback_question.question


class SwsPasiEvent(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    constructed_event_id = models.CharField(max_length=255)
    event_name = models.CharField(max_length=255)
    event_created_at = models.DateTimeField(null=True, blank=True)
    age = models.ForeignKey(Age, on_delete=models.SET_NULL, null=True, blank=True)
    language = models.ForeignKey(Language, on_delete=models.SET_NULL, null=True, blank=True)
    gender = models.ForeignKey(Gender, on_delete=models.SET_NULL, null=True, blank=True)
    device_id = models.CharField(max_length=255, null=True, blank=True)
    app_id = models.CharField(max_length=255, null=True, blank=True)
    organisation = models.ForeignKey(Organisation, on_delete=models.SET_NULL, null=True, blank=True)
    destination = models.ForeignKey(
        Country, on_delete=models.SET_NULL, null=True, blank=True, related_name="sws_pasi_destination"
    )

    def __str__(self) -> str:
        return self.event_name


class LinksClickEvent(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    event_date = models.DateField()
    event_name = models.CharField(max_length=100)
    link = models.CharField(max_length=200, null=True, blank=True)

    def __str__(self) -> str:
        return self.link


class TelephoneClickEvent(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    event_date = models.DateField()
    event_name = models.CharField(max_length=100)
    link = models.CharField(max_length=200, null=True, blank=True)

    def __str__(self) -> str:
        return self.link


class BigqueryHomepageEventData(models.Model):
    event_date = models.DateField()
    device_id = models.CharField(max_length=255, null=True, blank=True)
    app_id = models.CharField(max_length=255, null=True, blank=True)
    language = models.ForeignKey(Language, on_delete=models.SET_NULL, null=True, blank=True)
    locale = models.CharField(max_length=255, null=True, blank=True)
    destination = models.ForeignKey(
        Country, on_delete=models.SET_NULL, null=True, blank=True, related_name="homepage_event_destination"
    )
    age = models.ForeignKey(Age, on_delete=models.SET_NULL, null=True, blank=True)
    gender = models.ForeignKey(Gender, on_delete=models.SET_NULL, null=True, blank=True)
    immigration_status = models.ForeignKey(
        ImmigrationStatus, on_delete=models.SET_NULL, null=True, blank=True
    )
    organisation = models.ForeignKey(Organisation, on_delete=models.SET_NULL, null=True, blank=True)
    organisation_code = models.CharField(max_length=255, null=True, blank=True)
    is_myvoice_organisation = models.BooleanField(default=False)

    def __str__(self):
        return f"Homepage Event on {self.event_date} for Device {self.device_id}"


class ReportIssueSubmittedEvent(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    event_date = models.DateTimeField()
    event_name = models.CharField(max_length=100)
    age = models.ForeignKey("preference.Age", on_delete=models.SET_NULL, null=True, blank=True)
    language = models.ForeignKey("preference.Language", on_delete=models.SET_NULL, null=True, blank=True)
    gender = models.ForeignKey("preference.Gender", on_delete=models.SET_NULL, null=True, blank=True)
    device_id = models.CharField(max_length=255, null=True, blank=True)
    app_id = models.CharField(max_length=255, null=True, blank=True)
    organisation_access_code = models.CharField(max_length=255, null=True, blank=True)
    organisation_code = models.CharField(max_length=255, null=True, blank=True)
    organisation = models.ForeignKey(
        "preference.Organisation", on_delete=models.SET_NULL, null=True, blank=True
    )
    locale = models.CharField(max_length=255, null=True, blank=True)
    destination_state = models.ForeignKey(
        "preference.CountryState", on_delete=models.SET_NULL, null=True, blank=True
    )
    destination = models.ForeignKey(
        "preference.Country",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="report_issue_destination",
    )
    origin = models.ForeignKey(
        "preference.Country",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="report_issue_origin",
    )
    route = models.ForeignKey("preference.Route", on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"Report Issue on {self.event_date} by {self.device_id}"

from django.db import models

class UserLocation(models.Model):
    country = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    region = models.CharField(max_length=100)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    user_count = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.city}, {self.country} ({self.user_count} users)"
