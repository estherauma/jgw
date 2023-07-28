import django_filters

from .models import MessagingQuestionStandard

class MessagingQuestionFilter(django_filters.FilterSet):
    class Meta:
        model = MessagingQuestionStandard
        fields = ["origin__name", "destination__name"]