from django.db.models import Count, Sum

from events.models import BigQueryChaptersData, BigQueryFirstOpenHomepageData


def get_chapters_counts():
    chapter_sums = BigQueryChaptersData.objects.values('chapters').annotate(sum_count=Sum('count'))
    return chapter_sums

def get_chapters_users():
    chapter_sums = BigQueryChaptersData.objects.values('chapters').annotate(sum_count=Sum('users'))
    return chapter_sums

def get_firstopen_homepage_data():
    queryset = BigQueryFirstOpenHomepageData.objects.all()
    return queryset