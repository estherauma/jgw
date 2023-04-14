from django.db import models


class TranslatedQuestionText(models.Model):
    prismic_id = models.CharField(max_length=64, null=False)
    translation = models.TextField(null=True)
    original_text = models.TextField(null=True)


class TranslatedResponseText(models.Model):
    original_text = models.TextField(null=False)
    translation = models.TextField(null=True)


class TranslatedText(models.Model):
    original_text = models.TextField(null=False)
    translation = models.TextField(null=True)


class Scheme(models.Model):
    name = models.CharField(max_length=128, null=False, blank=False)


class Factory(models.Model):
    name = models.CharField(max_length=128, null=False, blank=False)
    scheme = models.ForeignKey(
        to="Scheme", related_name="factories", on_delete=models.CASCADE, null=True, blank=True, default=None
    )


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
    origin_country = models.CharField(max_length=255)
    destination_country = models.CharField(max_length=255)
    origin_coordinates = models.CharField(max_length=255)
    destination_coordinates = models.CharField(max_length=255)

    def _coordinates_as_list(self, coordinates_str):
        coords_str = coordinates_str.strip('[]')
        coords_list = coords_str.split(',')
        coords_float = [float(coord) for coord in coords_list]
        return coords_float

    @property
    def origin_coordinates_as_list(self):
        return self._coordinates_as_list(self.origin_coordinates)

    @property
    def destination_coordinates_as_list(self):
        return self._coordinates_as_list(self.destination_coordinates)

    def __str__(self):
        return f"{self.origin_country} to {self.destination_country}: {self.origin_coordinates_as_list} - {self.destination_coordinates_as_list}"

