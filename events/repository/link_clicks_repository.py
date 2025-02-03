from django.db.models import Count, F
from events.filters import generic_link_clicked_filtered_queryset
from events.models import LinksClickEvent

def get_link_clicked_data(**filters):
    link_clicked_queryset = generic_link_clicked_filtered_queryset(
        queryset=LinksClickEvent.objects.all(), **filters
    )

    link_clicks = (
        link_clicked_queryset.values("link")
        .annotate(count=Count("event_name"))
        .exclude(link=None)
        .order_by("-count")
    )

    links = []
    counts = []
    
    for entry in link_clicks:
        links.append(entry["link"])
        counts.append(entry["count"])

    return {"labels": links, "link": counts}