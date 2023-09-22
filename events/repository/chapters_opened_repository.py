
from django.db.models import Count, F
from common.helpers.preference_helpers.events import events_name_patterns_to_replace

from events.models import ChaptersOpened


def get_chapters_opened():
    chapters_opened = ChaptersOpened.objects.values('event_name').annotate(count=Count('event_name')).order_by('-count')
    sums = {}
    for entry in chapters_opened:
        event_name = entry['event_name']
        if event_name in events_name_patterns_to_replace:
            entry['event_name'] = events_name_patterns_to_replace[event_name]
        if entry['event_name'] not in sums:
            sums[entry['event_name']] = 0
        sums[entry['event_name']] += entry['count']

    return {
        "labels": list(sums.keys()),
        "counts": list(sums.values())
    }