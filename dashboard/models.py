from django.db import models


class TranslatedQuestionText(models.Model):
    prismic_id = models.CharField(max_length=64, null=False)
    question_text = models.TextField()


class TranslatedResponseText(models.Model):
    original_text = models.TextField(null=False)
    translation = models.TextField(null=False)


class TranslatedText(models.Model):
    original_text = models.TextField(null=False)
    translation = models.TextField(null=False)
