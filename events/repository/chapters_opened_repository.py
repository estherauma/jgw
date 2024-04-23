from django.db.models import Count, F
from common.helpers.preference_helpers.events import events_name_patterns_to_replace
from events.filters import generic_chapters_opened_filtered_queryset

from events.models import ChaptersOpened


def get_chapters_opened_unique_by_users(**filters):
    chapters_opened_queryset = generic_chapters_opened_filtered_queryset(
        queryset=ChaptersOpened.objects.all(), **filters
    )

    chapters_opened = (
        chapters_opened_queryset.exclude(device_id__isnull=True)
        .values("event_name", "device_id")
        .annotate(count=Count("id"))
        .order_by("-count")
    )

    sums = {}
    for entry in chapters_opened:
        event_name = entry["event_name"]
        if event_name in events_name_patterns_to_replace:
            entry["event_name"] = events_name_patterns_to_replace[event_name]
        if entry["event_name"] not in sums:
            sums[entry["event_name"]] = 0
        sums[entry["event_name"]] += entry["count"]
    sorted_sums = dict(sorted(sums.items(), key=lambda x: x[1], reverse=True))
    return {"labels": list(sorted_sums.keys()), "counts": list(sorted_sums.values())}


def get_chapters_opened(**filters):
    chapters_opened_queryset = generic_chapters_opened_filtered_queryset(
        queryset=ChaptersOpened.objects.all(), **filters
    )

    chapters_opened = (
        chapters_opened_queryset.values("event_name").annotate(count=Count("event_name")).order_by("-count")
    )

    sums = {}
    for entry in chapters_opened:
        event_name = entry["event_name"]
        if event_name in events_name_patterns_to_replace:
            entry["event_name"] = events_name_patterns_to_replace[event_name]
        if entry["event_name"] not in sums:
            sums[entry["event_name"]] = 0
        sums[entry["event_name"]] += entry["count"]
    return {"labels": list(sums.keys()), "counts": list(sums.values())}
