from django.db.models import Count, F, Q
from events.filters import generic_chapters_opened_filtered_queryset

from events.models import ChaptersOpened


def _chapter_label(entry):
    """Resolve display label for a chapter row (immigration status title or chapter text)."""
    immigration = entry.get("immigration_status_chapter_text")
    chapter = entry.get("chapter_text")
    if immigration is not None:
        return immigration
    if chapter is not None:
        return chapter
    return "Others"


def _build_destination_origin_chapter_tree(entries):
    """
    Build a tree: destination -> origin -> chapter leaves with value (count).
    Returns list of destination nodes, each with children = list of origin nodes,
    each origin with children = list of { name, value } for chapters.
    """
    tree = {}

    for entry in entries:
        dest_name = entry.get("destination_text") or "Others"
        origin_name = entry.get("origin_text") or "Others"
        chapter_name = _chapter_label(entry)
        count = entry["count"]

        if dest_name not in tree:
            tree[dest_name] = {}
        if origin_name not in tree[dest_name]:
            tree[dest_name][origin_name] = {}
        tree[dest_name][origin_name][chapter_name] = tree[dest_name][origin_name].get(chapter_name, 0) + count

    destination_nodes = []
    for dest_name in sorted(tree.keys()):
        origin_children = []
        for origin_name in sorted(tree[dest_name].keys()):
            chapter_children = [
                {"name": ch_name, "value": ch_count}
                for ch_name, ch_count in sorted(tree[dest_name][origin_name].items(), key=lambda x: -x[1])
            ]
            origin_children.append({"name": origin_name, "children": chapter_children})
        destination_nodes.append({"name": dest_name, "children": origin_children})

    return destination_nodes


def get_chapters_opened_data(**filters):
    """
    Return chapter opened data as a tree for ECharts tree chart.
    Root -> [Total views, Unique views] -> destination -> origin -> chapter titles with value (count).
    """
    chapters_opened_queryset = generic_chapters_opened_filtered_queryset(
        queryset=ChaptersOpened.objects.exclude(device_id__isnull=True), **filters
    )

    chapters_opened_with_labels_queryset = chapters_opened_queryset.annotate(
        chapter_text=F("chapter__chapter_text"),
        origin_text=F("chapter__origin__name"),
        destination_text=F("chapter__destination__name"),
        number_key=F("chapter__number_key"),
        immigration_status_chapter_text=F("immigration_status_chapter_title__chapter_title"),
    ).filter(Q(immigration_status_chapter_text__isnull=False) | Q(chapter_text__isnull=False))

    chapters_opened_all = (
        chapters_opened_with_labels_queryset
        .values("chapter_text", "number_key", "immigration_status_chapter_text", "origin_text", "destination_text")
        .annotate(count=Count("event_name"))
        .order_by("-count")
    )

    chapters_opened_unique = (
        chapters_opened_with_labels_queryset
        .values("chapter_text", "number_key", "immigration_status_chapter_text", "origin_text", "destination_text")
        .annotate(count=Count("device_id", distinct=True))
        .order_by("-count")
    )

    all_entries = list(chapters_opened_all)
    unique_entries = list(chapters_opened_unique)

    total_views_tree = _build_destination_origin_chapter_tree(all_entries)
    unique_views_tree = _build_destination_origin_chapter_tree(unique_entries)

    tree = {
        "name": "views",
        "children": [
            {"name": "Total views", "children": total_views_tree},
            {"name": "Unique views", "children": unique_views_tree},
        ],
    }

    sums_all = {}
    sums_unique = {}
    for entry in all_entries:
        key = _chapter_label(entry)
        sums_all[key] = sums_all.get(key, 0) + entry["count"]
    for entry in unique_entries:
        key = _chapter_label(entry)
        sums_unique[key] = sums_unique.get(key, 0) + entry["count"]
    all_labels = [k if k is not None else "Others" for k in sums_all.keys()]
    all_counts = [sums_all.get(label, 0) for label in all_labels]
    unique_counts = [sums_unique.get(label, 0) for label in all_labels]

    return {
        "tree": tree,
        "labels": all_labels,
        "chapteropened_all": all_counts,
        "chapteropened_unique": unique_counts,
    }
