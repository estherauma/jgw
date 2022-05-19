from django.db import models

# Create your models here.
class TranslatedQuestionText(models.Model):
    prismic_id = models.CharField(max_length=64, null=False)
    question_text = models.TextField()


class TranslatedAgeText(models.Model):
    original_text = models.CharField(max_length=64, null=False)
    translation = models.CharField(max_length=128, null=False)


class TranslatedGenderText(models.Model):
    original_text = models.CharField(max_length=64, null=False)
    translation = models.CharField(max_length=128, null=False)


class TranslatedLanguageText(models.Model):
    original_text = models.CharField(max_length=64, null=False)
    translation = models.CharField(max_length=128, null=False)


class TranslatedResponseText(models.Model):
    original_text = models.TextField(null=False)
    translation = models.TextField(null=False)



class TranslatedHearAboutUsText(models.Model):
    original_text = models.TextField(null=False)
    translation = models.TextField(null=False)



class TranslatedSectorOfWorkText(models.Model):
    original_text = models.TextField(null=False)
    translation = models.TextField(null=False)