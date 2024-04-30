from django.db.models import Count, F
from common.helpers.preference_helpers.events import events_name_patterns_to_replace
from events.filters import generic_chapters_opened_filtered_queryset

from events.models import Chapter, ChaptersOpened


def get_chapters_opened_unique_by_users(**filters):
    chapters_opened_queryset = generic_chapters_opened_filtered_queryset(
        queryset=ChaptersOpened.objects.all(), **filters
    )

    chapters_opened = (
        chapters_opened_queryset.exclude(device_id__isnull=True)
        .values("chapter__chapter_text", "chapter__number_key", "device_id")
        .annotate(count=Count("id"))
        .order_by("-count")
    )

    sums = {}
    for entry in chapters_opened:
        chapter_text = entry["chapter__chapter_text"]
        number_key = entry["chapter__number_key"]
        count = entry["count"]

        if number_key:
            chapter = Chapter.objects.filter(number_key=number_key, destination__name='malaysia').first()
            if chapter:
                chapter_text = chapter.chapter_text

        if chapter_text in sums:
            sums[chapter_text] += count
        else:
            sums[chapter_text] = count

    sorted_sums = dict(sorted(sums.items(), key=lambda x: x[1], reverse=True))

    if None in sorted_sums:
        del sorted_sums[None]
    return {"labels": list(sorted_sums.keys()), "counts": list(sorted_sums.values())}

def get_chapters_opened(**filters):
    chapters_opened_queryset = generic_chapters_opened_filtered_queryset(
        queryset=ChaptersOpened.objects.all(), **filters
    )

    chapters_opened = (
        chapters_opened_queryset
        .values("chapter__chapter_text", "chapter__number_key")
        .annotate(count=Count("event_name"))
        .order_by("-count")
    )

    sums = {}
    for entry in chapters_opened:
        chapter_text = entry["chapter__chapter_text"]
        number_key = entry["chapter__number_key"]
        count = entry["count"]
        if number_key:
            chapter = Chapter.objects.filter(number_key=number_key, destination__name='malaysia').first()
            if chapter:
                chapter_text = chapter.chapter_text
        if chapter_text in sums:
            sums[chapter_text] += count
        else:
            sums[chapter_text] = count
    if None in sums:
        del sums[None]

    return {"labels": list(sums.keys()), "counts": list(sums.values())}