"""Build User Insights page context from UserInsightsReport / UserInsightsIndicator."""

from django.db.models import Prefetch

from question.models import UserInsightsIndicator, UserInsightsReport


def _placeholder_donut(indicator):
    """Donut segment values until analytics are wired to lead responses."""
    return {
        "title": indicator.name,
        "needs_action": 0,
        "on_track": 0,
        "no_response": 100,
        "breakdown_index": indicator.breakdown_index,
    }


def _donut_row_indicators(indicators):
    """Active indicators on this report that appear in the donut row."""
    return [
        indicator
        for indicator in indicators
        if indicator.show_on_donut and indicator.donut_slot is not None
    ]


def build_donuts_for_indicators(indicators):
    """
    Build donut chart payload ordered by donut_slot.

    Returns (donuts list indexed by slot, donut_count).
    """
    donut_indicators = _donut_row_indicators(indicators)
    if not donut_indicators:
        return [], 0

    max_slot = max(i.donut_slot for i in donut_indicators)
    donuts = []
    for slot in range(max_slot + 1):
        indicator = next((i for i in donut_indicators if i.donut_slot == slot), None)
        donuts.append(_placeholder_donut(indicator) if indicator else None)
    return donuts, max_slot + 1


def build_indicator_options(indicators, indicator_detail_builder):
    """Donut-row indicators only (active, show_on_donut) for filter + breakdown."""
    options = []
    for indicator in sorted(
        _donut_row_indicators(indicators),
        key=lambda i: (i.donut_slot, i.breakdown_index, i.display_order, i.name),
    ):
        options.append(
            {
                "breakdown_index": indicator.breakdown_index,
                "name": indicator.name,
                "color": indicator.color,
                "show_on_donut": True,
                "donut_slot": indicator.donut_slot,
                "detail": indicator_detail_builder(indicator),
            }
        )
    return options


def build_report_context_entry(report, indicator_detail_builder):
    """Merge UserInsightsReport ORM instance with chart/breakdown structures for templates."""
    indicators = list(report.indicators.all())
    donuts, donut_count = build_donuts_for_indicators(indicators)
    indicator_options = build_indicator_options(indicators, indicator_detail_builder)
    return {
        "id": report.slug,
        "title": report.title,
        "description": report.description,
        "hint": report.hint,
        "pdf_label": report.pdf_label,
        "breakdown_header": report.breakdown_header,
        "donuts": donuts,
        "donut_count": donut_count,
        "indicator_options": indicator_options,
    }


def load_active_user_insights_reports():
    indicator_qs = (
        UserInsightsIndicator.objects.filter(is_active=True)
        .select_related("report")
        .prefetch_related(
            "indicator_inline_questions__question",
            "indicator_messaging_questions__question",
        )
        .order_by("breakdown_index", "display_order", "name")
    )
    return list(
        UserInsightsReport.objects.filter(is_active=True)
        .prefetch_related(Prefetch("indicators", queryset=indicator_qs))
        .order_by("display_order", "title")
    )
