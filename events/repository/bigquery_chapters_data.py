from events.models import BigQueryChaptersData


def get_user_per_chapters():
    queryset = BigQueryChaptersData.objects.all()
    return queryset