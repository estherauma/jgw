from django.db.models import Q

from django.db import models


class TranslatedQuestionText(models.Model):
    prismic_id = models.CharField(max_length=64, null=False)
    translation = models.TextField(null=True)
    original_text = models.TextField(null=True)


class TranslatedResponseText(models.Model):
    original_text = models.TextField(null=False)
    translation = models.TextField(null=True)
    
    def __str__(self):
        return f"{self.original_text} -> {self.translation}"


class TranslatedText(models.Model):
    original_text = models.TextField(null=False)
    translation = models.TextField(null=True)

    def __str__(self):
        return f"{self.original_text} -> {self.translation}"




class Scheme(models.Model):
    name = models.CharField(max_length=128, null=False, blank=False)

    def __str__(self):
        return self.name


class Factory(models.Model):
    name = models.CharField(max_length=128, null=False, blank=False)
    scheme = models.ForeignKey(
        to="Scheme", related_name="factories", on_delete=models.CASCADE, null=True, blank=True, default=None
    )

    def __str__(self):
        return f"{self.name}"


class JGWCache(models.Model):
    class Meta:
        ordering = ("-date_created",)

    category = models.CharField(max_length=128, null=False, blank=False)
    is_cleaned = models.BooleanField(default=False, null=False, blank=False)
    data = models.JSONField(null=False)
    date_created = models.DateField(auto_now_add=True)
    date_modified = models.DateField(auto_now=True)

    def __str__(self) -> str:
        return f'{self.category} - {self.date_created} - {self.is_cleaned}'


class Route(models.Model):
    origin_country = models.CharField(
        max_length=255,
        blank=False, null=False,
        verbose_name="Origin Country",
        help_text="Enter the name of the country for the origin location"
    )
    destination_country = models.CharField(
        max_length=255,
        blank=False, null=False,
        verbose_name="Destination Country",
        help_text="Enter the name of the country for the destination location"
    )
    origin_longitude = models.FloatField(
        blank=True, null=True,
        verbose_name="Origin Longitude",
        help_text="Enter the longitude of the origin location"
    )
    origin_latitude = models.FloatField(
        blank=True, null=True,
        verbose_name="Origin Latitude",
        help_text="Enter the latitude of the origin location"
    )
    destination_longitude = models.FloatField(
        blank=True, null=True,
        verbose_name="Destination Longitude",
        help_text="Enter the longitude of the destination location"
    )
    destination_latitude = models.FloatField(
        blank=True, null=True,
        verbose_name="Destination Latitude",
        help_text="Enter the latitude of the destination location"
    )
    active = models.BooleanField(default=False)

    @classmethod
    def get_routes(cls):
        routes = []
        for route in cls.objects.filter(
            Q(origin_longitude__isnull=False),
            Q(origin_latitude__isnull=False),
            Q(destination_longitude__isnull=False),
            Q(destination_latitude__isnull=False),
            active=True
        ):
            routes.append({
                "from": route.origin_country,
                "to": route.destination_country,
                "from_coords": [route.origin_latitude, route.origin_longitude],
                "to_coords": [route.destination_latitude, route.destination_longitude]
            })
        return routes

    def __str__(self):
        return f"Route from {self.origin_country} to {self.destination_country}"


