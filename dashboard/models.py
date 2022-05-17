from django.db import models

# Create your models here.
class TranslatedQuestionText(models.Model):
    prismic_id = models.CharField(max_length=64, null=False)
    question_text = models.TextField()
