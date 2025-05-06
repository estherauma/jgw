from django.db.models import Count, F
from events.filters import generic_chapters_opened_filtered_queryset

from events.models import ChaptersOpened


def get_chapters_opened_data(**filters):
    chapters_opened_queryset = generic_chapters_opened_filtered_queryset(
        queryset=ChaptersOpened.objects.exclude(device_id__isnull=True), **filters
    )

    chapters_opened_all = (
        chapters_opened_queryset.annotate(
            chapter_text=F("chapter__chapter_text"),
            number_key=F("chapter__number_key"),
            immigration_status_chapter_text=F("immigration_status_chapter_title__chapter_title"),
        )
        .values("chapter_text", "number_key", "immigration_status_chapter_text")
        .annotate(count=Count("event_name"))
        .order_by("-count")
    )

    chapters_opened_unique = (
        chapters_opened_queryset.annotate(
            chapter_text=F("chapter__chapter_text"),
            number_key=F("chapter__number_key"),
            immigration_status_chapter_text=F("immigration_status_chapter_title__chapter_title"),
        )
        .values("chapter_text", "number_key", "immigration_status_chapter_text")
        .annotate(count=Count("device_id", distinct=True))
        .order_by("-count")
    )

    sums_all = {}
    for entry in chapters_opened_all:
        chapter_text = entry["chapter_text"]
        immigration_status_chapter_text = entry["immigration_status_chapter_text"]
        number_key = entry["number_key"]
        count = entry["count"]
        key = "Others" if immigration_status_chapter_text is None and chapter_text is None else (immigration_status_chapter_text if immigration_status_chapter_text is not None else chapter_text)
        sums_all.setdefault(key, 0)
        sums_all[key] += count

    sums_unique = {}
    for entry in chapters_opened_unique:
        chapter_text = entry["chapter_text"]
        immigration_status_chapter_text = entry["immigration_status_chapter_text"]
        number_key = entry["number_key"]
        count = entry["count"]
        key = "Others" if immigration_status_chapter_text is None and chapter_text is None else (immigration_status_chapter_text if immigration_status_chapter_text is not None else chapter_text)
        sums_unique.setdefault(key, 0)
        sums_unique[key] += count

    all_labels = [label if label is not None else "Others" for label in sums_all.keys()]
    unique_counts = [sums_unique.get(label, 0) for label in all_labels]
    all_counts = [sums_all.get(label, 0) for label in all_labels]

    print("all_labels", all_labels)
    print("unique_counts", unique_counts)
    print("all_counts", all_counts)

    return {"labels": all_labels, "chapteropened_unique": unique_counts, "chapteropened_all": all_counts}
