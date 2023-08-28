from events.models import BigQueryChaptersData, BigQueryFirstOpenHomepageData


def get_user_per_chapters():
    queryset = BigQueryChaptersData.objects.all()
    return queryset

def get_firstopen_homepage_data():
    queryset = BigQueryFirstOpenHomepageData.objects.all()
    return queryset