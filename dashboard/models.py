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
