import json
from datetime import datetime
from django.shortcuts import render
from common.const.value_const import COUNTRY_COORDS
from common.utils.request import get_form_filter_params
from openpyxl.styles import Alignment, Font

import openpyxl
from openpyxl.utils import get_column_letter
from django.http import HttpResponse

from core.forms import GenericFilterForm, DateRangeForm
from core.logic.file_export import generate_and_export_excel
from events.repository.bigquery_homepage_events_repository import (
    get_monthly_active_user_count,
    get_total_active_user_within_period,
    get_user_counts_by_geo_country,
)
from events.repository.bigquery_sws_pasi_repository import get_total_dynamic_link_usage
from events.repository.link_clicks_repository import get_link_clicked_data
from help_contacts.repository.help_contacts_data import get_help_contacts_between_dates
from preference.repository.preference_repository import (
    extract_preference_for_export,
    get_cumulative_monthly_new_users,
    get_pay_calculator_statistics,
    get_preferences_by_sectors,
    get_returning_users_grouped_by_original_device_id,
    get_sws_workcodes_with_access_code,
    get_users_by_country_state,
    preference_stats_for_export,
    preferences_by_age,
    preferences_by_destination,
    preferences_by_gender,
    preferences_by_language,
    preferences_by_organisation,
    preferences_by_origin,
    preferences_count,
    get_user_counts_by_origin_destination,
    preferences_by_immigration_status,
    get_user_counts_by_geolocation,
    get_preferences_by_device_id,
)
from users.utils import get_user_organisations
from django.core.serializers.json import DjangoJSONEncoder
from django.contrib.auth.decorators import login_required
from django.utils.translation import gettext as _
from django.db import transaction
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from preference.dashboard_config import (
    CHART_DEFINITIONS,
    get_default_chart_settings,
    get_default_dashboard_preferences,
)
from preference.models import DashboardPreferences, ChartSettings
from user_management.permissions import is_flag_active
import logging


@login_required
def user_insights(request):
    """User Insights page."""
    figma_colors = {"needs_action": "#9e1b32", "on_track": "#99b945", "no_response": "#d1d5db"}
    legend_labels = {
        "needs_action": str(_("userInsightsLegendNeedsAction")),
        "on_track": str(_("userInsightsLegendOnTrack")),
        "no_response": str(_("userInsightsLegendNoResponse")),
    }

    def _d(title, na, ot, breakdown_index):
        nr = 100 - na - ot
        return {
            "title": str(title),
            "needs_action": na,
            "on_track": ot,
            "no_response": nr,
            "breakdown_index": breakdown_index,
        }

    def _br(name, color):
        return {"name": str(name), "color": color}

    donuts_early = [
        _d(_("userInsightsDonutAbuseVulnerability"), 8, 12, 0),
        _d(_("userInsightsDonutAbusiveConditions"), 6, 15, 9),
        _d(_("userInsightsDonutDeception"), 10, 14, 1),
        _d(_("userInsightsDonutIdentityDocs"), 7, 11, 6),
        _d(_("userInsightsDonutIntimidation"), 9, 13, 5),
    ]
    donuts_decent = [
        _d(_("userInsightsDEDonutFairWages"), 10, 16, 0),
        _d(_("userInsightsDEDonutWorkingHours"), 7, 13, 1),
        _d(_("userInsightsDEDonutHealthSafety"), 9, 12, 2),
        _d(_("userInsightsDEDonutContracts"), 6, 14, 3),
        _d(_("userInsightsDEDonutWorkLifeBalance"), 8, 11, 5),
    ]
    donuts_responsible = [
        _d(_("userInsightsRRDonutRecruitment"), 11, 14, 5),
        _d(_("userInsightsRRDonutOnboarding"), 8, 17, 2),
        _d(_("userInsightsRRDonutEmployment"), 9, 15, 7),
        _d(_("userInsightsRRDonutAddressingIssues"), 7, 12, 3),
    ]

    breakdown_early = [
        _br(_("userInsightsIndicatorAbuseVulnerability"), "#e67e22"),
        _br(_("userInsightsIndicatorDeception"), "#1abc9c"),
        _br(_("userInsightsIndicatorRestrictionMovement"), "#f1c40f"),
        _br(_("userInsightsIndicatorIsolation"), "#3498db"),
        _br(_("userInsightsIndicatorPhysicalSexualViolence"), "#e74c3c"),
        _br(_("userInsightsIndicatorIntimidationThreats"), "#9b59b6"),
        _br(_("userInsightsIndicatorRetentionIdentity"), "#e91e63"),
        _br(_("userInsightsIndicatorWithholdingWages"), "#00bcd4"),
        _br(_("userInsightsIndicatorDebtBondage"), "#795548"),
        _br(_("userInsightsIndicatorAbusiveConditions"), "#607d8b"),
        _br(_("userInsightsIndicatorExcessiveOvertime"), "#ff5722"),
    ]
    breakdown_decent = [
        _br(_("userInsightsDEIndDecentWork"), "#2980b9"),
        _br(_("userInsightsDEIndEqualTreatment"), "#8e44ad"),
        _br(_("userInsightsDEIndSafeWorkplace"), "#16a085"),
        _br(_("userInsightsDEIndSocialProtection"), "#d35400"),
        _br(_("userInsightsDEIndDialogue"), "#c0392b"),
        _br(_("userInsightsDEIndCareerDevelopment"), "#27ae60"),
    ]
    breakdown_responsible = [
        _br(_("userInsightsRRIndAccommodation"), "#e67e22"),
        _br(_("userInsightsRRIndFairTreatment"), "#2ecc71"),
        _br(_("userInsightsRRIndOnboarding"), "#3498db"),
        _br(_("userInsightsRRIndAddressingIssues"), "#9b59b6"),
        _br(_("userInsightsRRIndChangingJob"), "#e74c3c"),
        _br(_("userInsightsRRIndRecruitment"), "#1abc9c"),
        _br(_("userInsightsRRIndTravel"), "#f39c12"),
        _br(_("userInsightsRRIndEmployment"), "#34495e"),
    ]

    def _mock_follow_up_option(label, count, total, selected=False, follow_up=None):
        option = {
            "id": label.lower().replace(" ", "-").replace("$", "").replace(",", ""),
            "label": label,
            "count": count,
            "total": total,
            "selected": selected,
        }
        if follow_up:
            option["follow_up"] = follow_up
        return option

    def _mock_follow_up_question(code, text, options):
        return {"code": code, "text": text, "options": options}

    def _mock_lead_question(
        number, qid, text, total, responses, expanded=False, response_type="choice", active=False
    ):
        return {
            "id": qid,
            "number": number,
            "text": text,
            "total": total,
            "expanded": expanded,
            "responses": responses,
            "response_type": response_type,
            "active": active,
        }

    def _mock_text_response_item(response_id, native, translation, starred=True):
        return {
            "id": response_id,
            "label": f"Response #{response_id}",
            "native": native,
            "translation": translation,
            "starred": starred,
        }

    def _mock_all_responses_row(date, response_id, native, translation=None, starred=False):
        return {
            "date": date,
            "id": response_id,
            "label": f"#{response_id}",
            "native": native,
            "translation": translation,
            "starred": starred,
        }

    def _mock_all_responses_table_rows():
        na = str(_("userInsightsTranslationNA"))
        return [
            _mock_all_responses_row(
                "05/12/2025",
                "589323",
                str(_("userInsightsMockNativeTable1")),
                str(_("userInsightsMockTranslationApp")),
                starred=True,
            ),
            _mock_all_responses_row(
                "04/12/2025",
                "589301",
                str(_("userInsightsMockNativeTable2")),
                str(_("userInsightsMockTranslation2")),
            ),
            _mock_all_responses_row(
                "03/12/2025",
                "589288",
                str(_("userInsightsMockNativeTable3")),
                str(_("userInsightsMockTranslation3")),
            ),
            _mock_all_responses_row(
                "02/12/2025",
                "589271",
                str(_("userInsightsMockNative1")),
                str(_("userInsightsMockTranslation1")),
            ),
            _mock_all_responses_row(
                "01/12/2025",
                "589254",
                str(_("userInsightsMockNativeTable4")),
                na,
            ),
            _mock_all_responses_row(
                "30/11/2025",
                "589240",
                str(_("userInsightsMockNativeTable5")),
                str(_("userInsightsMockTranslationTable5")),
            ),
            _mock_all_responses_row(
                "29/11/2025",
                "589221",
                str(_("userInsightsMockNative2")),
                str(_("userInsightsMockTranslationApp")),
            ),
            _mock_all_responses_row(
                "28/11/2025",
                "589198",
                str(_("userInsightsMockNativeTable6")),
                str(_("userInsightsMockTranslationTable6")),
                starred=True,
            ),
        ]

    def _mock_open_text_detail(question_label, indicator_name):
        text_crumb = str(_("userInsightsMockTextResponseCrumb")) % {"question": question_label}
        return {
            "breadcrumb": [
                text_crumb,
                str(_("userInsightsStarredResponses")),
            ],
            "starred_count": 22,
            "total_count": 198,
            "all_responses": {
                "breadcrumb": [
                    indicator_name,
                    text_crumb,
                    str(_("userInsightsAllResponses")),
                ],
                "total_count": 198,
                "rows": _mock_all_responses_table_rows(),
            },
            "responses": [
                _mock_text_response_item(
                    "58203",
                    str(_("userInsightsMockNative1")),
                    str(_("userInsightsMockTranslation1")),
                ),
                _mock_text_response_item(
                    "58197",
                    str(_("userInsightsMockNative2")),
                    str(_("userInsightsMockTranslation2")),
                ),
                _mock_text_response_item(
                    "58188",
                    str(_("userInsightsMockNative3")),
                    str(_("userInsightsMockTranslation3")),
                    starred=False,
                ),
            ],
        }

    def _mock_open_text_lead(
        number, qid, text, indicator_name, expanded=False, active=False
    ):
        question_label = f"Q{number}"
        lead = _mock_lead_question(
            number,
            qid,
            text,
            None,
            [],
            expanded=expanded,
            response_type="open_text",
            active=active,
        )
        lead["text_detail"] = _mock_open_text_detail(question_label, indicator_name)
        return lead

    def _mock_sunburst_tree(lead_question_text, follow_up_1a_text, follow_up_1b_text):
        """Sunburst nodes include question text for per-layer hover tooltips."""
        return [
            {
                "name": str(_("userInsightsMockAnswerYes")),
                "value": 62,
                "question": lead_question_text,
                "itemStyle": {"color": "#9e1b32"},
                "children": [
                    {
                        "name": str(_("userInsightsMockWhoAgent")),
                        "value": 10,
                        "question": follow_up_1a_text,
                        "itemStyle": {"color": "#7a1530"},
                        "children": [
                            {
                                "name": str(_("userInsightsMockAmountLt500")),
                                "value": 2,
                                "question": follow_up_1b_text,
                                "itemStyle": {"color": "#e8a4b8"},
                            },
                            {
                                "name": str(_("userInsightsMockAmount5001k")),
                                "value": 1,
                                "question": follow_up_1b_text,
                                "itemStyle": {"color": "#f0c4d0"},
                            },
                            {
                                "name": str(_("userInsightsMockAmount1k2k")),
                                "value": 1,
                                "question": follow_up_1b_text,
                                "itemStyle": {"color": "#f5d5de"},
                            },
                        ],
                    },
                    {
                        "name": str(_("userInsightsMockWhoEmployer")),
                        "value": 4,
                        "question": follow_up_1a_text,
                        "itemStyle": {"color": "#a82845"},
                    },
                    {
                        "name": str(_("userInsightsMockWhoRecruiter")),
                        "value": 6,
                        "question": follow_up_1a_text,
                        "itemStyle": {"color": "#b8324f"},
                    },
                    {
                        "name": str(_("userInsightsMockWhoSubagent")),
                        "value": 5,
                        "question": follow_up_1a_text,
                        "itemStyle": {"color": "#c43d59"},
                    },
                    {
                        "name": str(_("userInsightsMockWhoOther")),
                        "value": 3,
                        "question": follow_up_1a_text,
                        "itemStyle": {"color": "#d04863"},
                    },
                ],
            },
            {
                "name": str(_("userInsightsMockAnswerNo")),
                "value": 135,
                "question": lead_question_text,
                "itemStyle": {"color": "#c5d0dc"},
            },
        ]

    def _mock_indicator_detail(breakdown_index, report_id, indicator_name):
        """Nested lead / follow-up question mock for UI/UX; replace with DB later."""
        base_responses = 1166 - (breakdown_index * 53)
        panel_script_id = f"user-insights-drilldown-{report_id}-{breakdown_index}"

        follow_up_1b = _mock_follow_up_question(
            "1B",
            str(_("userInsightsMockQ1BFollowUp")),
            [
                _mock_follow_up_option(str(_("userInsightsMockAmount1k2k")), 1, 9),
                _mock_follow_up_option(str(_("userInsightsMockAmount5001k")), 1, 9),
                _mock_follow_up_option(
                    str(_("userInsightsMockAmountLt500")), 2, 9, selected=True
                ),
            ],
        )
        follow_up_1a = _mock_follow_up_question(
            "1A",
            str(_("userInsightsMockQ1AFollowUp")),
            [
                _mock_follow_up_option(
                    str(_("userInsightsMockWhoAgent")),
                    10,
                    28,
                    selected=True,
                    follow_up=follow_up_1b,
                ),
                _mock_follow_up_option(str(_("userInsightsMockWhoEmployer")), 4, 28),
                _mock_follow_up_option(str(_("userInsightsMockWhoOther")), 3, 28),
                _mock_follow_up_option(str(_("userInsightsMockWhoRecruiter")), 6, 28),
                _mock_follow_up_option(str(_("userInsightsMockWhoSubagent")), 5, 28),
            ],
        )
        lead_q1 = _mock_lead_question(
            1,
            "q1",
            str(_("userInsightsMockQ1Payments")),
            197,
            [
                {
                    "id": "yes",
                    "label": str(_("userInsightsMockAnswerYes")),
                    "count": 62,
                    "total": 197,
                    "selected": True,
                    "follow_up": follow_up_1a,
                },
                {
                    "id": "no",
                    "label": str(_("userInsightsMockAnswerNo")),
                    "count": 135,
                    "total": 197,
                    "selected": False,
                },
            ],
            expanded=True,
            active=True,
        )
        lead_q2 = _mock_open_text_lead(
            2,
            "q2",
            str(_("userInsightsMockQ2PaidFor")),
            indicator_name,
            expanded=False,
            active=False,
        )
        lead_q3 = _mock_open_text_lead(
            3,
            "q3",
            str(_("userInsightsMockQ3Contract")),
            indicator_name,
            expanded=False,
            active=True,
        )
        lead_questions = [lead_q1, lead_q2, lead_q3]

        return {
            "indicator_name": indicator_name,
            "user_responses": base_responses,
            "date_from": "2025-01-01",
            "date_to": "2025-01-01",
            "date_from_display": str(_("userInsightsMockDateFrom")),
            "date_to_display": str(_("userInsightsMockDateTo")),
            "panel_script_id": panel_script_id,
            "panel_dom_id": f"user-insights-panel-{report_id}-{breakdown_index}",
            "lead_questions": lead_questions,
            "choice_breadcrumb": [
                str(_("userInsightsMockAnswerYes")),
                str(_("userInsightsMockWhoAgent")),
                str(_("userInsightsMockAmountLt500")),
            ],
            "breadcrumb": lead_q3["text_detail"]["breadcrumb"],
            "sunburst": _mock_sunburst_tree(
                lead_q1["text"],
                follow_up_1a["text"],
                follow_up_1b["text"],
            ),
            "sunburst_highlight": str(_("userInsightsMockAmountLt500")),
        }

    def _indicator_options(donuts, breakdown_rows, report_id):
        """One entry per donut chart, aligned with dropdown and breakdown rows."""
        options = []
        for slot, donut in enumerate(donuts):
            breakdown_index = donut["breakdown_index"]
            row = breakdown_rows[breakdown_index]
            options.append(
                {
                    "breakdown_index": breakdown_index,
                    "name": row["name"],
                    "color": row["color"],
                    "donut_slot": slot,
                    "detail": _mock_indicator_detail(
                        breakdown_index, report_id, row["name"]
                    ),
                }
            )
        return options

    report_donuts = {
        "early_risk": donuts_early,
        "decent_employment": donuts_decent,
        "responsible_recruitment": donuts_responsible,
    }

    reports = [
        {
            "id": "early_risk",
            "title": _("userInsightsReportEarlyRisk"),
            "description": _("userInsightsReportEarlyRiskDesc"),
            "hint": _("userInsightsReportClickGraph"),
            "pdf_label": _("userInsightsDownloadPdfQuestions"),
            "breakdown_header": _("userInsightsIndicatorsHeader"),
            "breakdown_rows": breakdown_early,
            "donut_count": 5,
            "indicator_options": _indicator_options(donuts_early, breakdown_early, "early_risk"),
            "active": True,
        },
        {
            "id": "decent_employment",
            "title": _("userInsightsReportDecentEmployment"),
            "description": _("userInsightsReportDecentEmploymentDesc"),
            "hint": _("userInsightsReportDecentEmploymentHint"),
            "pdf_label": _("userInsightsDownloadPdfQuestions"),
            "breakdown_header": _("userInsightsDEIndicatorsHeader"),
            "breakdown_rows": breakdown_decent,
            "donut_count": 5,
            "indicator_options": _indicator_options(donuts_decent, breakdown_decent, "decent_employment"),
            "active": False,
        },
        {
            "id": "responsible_recruitment",
            "title": _("userInsightsReportResponsibleRecruitment"),
            "description": _("userInsightsReportResponsibleRecruitmentDesc"),
            "hint": _("userInsightsReportResponsibleRecruitmentHint"),
            "pdf_label": _("userInsightsDownloadPdfCategories"),
            "breakdown_header": _("userInsightsRRIndicatorsHeader"),
            "breakdown_rows": breakdown_responsible,
            "donut_count": 4,
            "indicator_options": _indicator_options(
                donuts_responsible, breakdown_responsible, "responsible_recruitment"
            ),
            "active": False,
        },
    ]

    chart_legends = [
        {"class": "needs-action", "label": legend_labels["needs_action"]},
        {"class": "on-track", "label": legend_labels["on_track"]},
        {"class": "no-response", "label": legend_labels["no_response"]},
    ]

    chart_payload = {
        "legends": legend_labels,
        "colors": figma_colors,
        "donuts": donuts_early,
        "by_report": {
            report_id: {
                "donuts": report_donuts[report_id],
                "donut_count": next(r["donut_count"] for r in reports if r["id"] == report_id),
                "indicator_options": next(
                    r["indicator_options"] for r in reports if r["id"] == report_id
                ),
                "breakdown_header": str(
                    next(r["breakdown_header"] for r in reports if r["id"] == report_id)
                ),
            }
            for report_id in report_donuts
        },
        "default_report_id": "early_risk",
    }

    active_report = next((r for r in reports if r.get("active")), reports[0])
    max_donut_slots = max(r["donut_count"] for r in reports)
    context = {
        "reports": reports,
        "chart_legends": chart_legends,
        "active_report": active_report,
        "donut_slots": list(range(max_donut_slots)),
        "chart_payload": chart_payload,
        "user_insights_all_responses_config": {
            "na_label": str(_("userInsightsTranslationNA")),
            "count_template": str(_("userInsightsAllResponsesCountTemplate")),
        },
    }
    return render(request, "preference/user_insights.html", context=context)


@login_required
def user_overview(request):
    form_filter_params = get_form_filter_params(request=request, form_class=GenericFilterForm)
    filters = form_filter_params["filters"]
    filter_form = form_filter_params["filter_form"]
    date_range_form = DateRangeForm()

    total_user_overview_responses = preferences_count(**filters, current_user=request.user)
    preferences_per_origin_country_responses = preferences_by_origin(**filters, current_user=request.user)
    preferences_per_destination_country_responses = preferences_by_destination(
        **filters, current_user=request.user
    )
    preferences_by_age_responses = preferences_by_age(**filters, current_user=request.user)
    preferences_by_gender_responses = preferences_by_gender(**filters, current_user=request.user)
    preferences_by_language_responses = preferences_by_language(**filters, current_user=request.user)
    preferences_by_organisation_responses = preferences_by_organisation(**filters, current_user=request.user)
    pref_cumulative_new_users = get_cumulative_monthly_new_users(**filters, current_user=request.user)
    users_by_country_state = get_users_by_country_state(**filters, current_user=request.user)
    preferences_by_sectors = get_preferences_by_sectors(**filters, current_user=request.user)
    sws_workcodes_with_access_code = get_sws_workcodes_with_access_code(**filters, current_user=request.user)
    monthly_active_users = get_monthly_active_user_count(**filters, current_user=request.user)
    total_active_users = get_total_active_user_within_period(**filters, current_user=request.user)
    user_counts_by_origin_destination = get_user_counts_by_origin_destination(
        **filters, current_user=request.user
    )
    user_counts_by_geolocation = get_user_counts_by_geolocation(**filters)
    
    country_coords = COUNTRY_COORDS
    pasi_downloads = (
        get_total_dynamic_link_usage(current_user=request.user)
        if not request.user.is_anonymous and request.user.role == "SCHEME"
        else 0
    )
    preferences_by_immigration_status_responses = preferences_by_immigration_status(
        **filters, current_user=request.user
    )
    link_clicks_data = get_link_clicked_data(**filters, current_user=request.user)
    user_counts_by_geo_country = get_user_counts_by_geo_country(**filters, current_user=request.user)

    # Get DashboardPreferences and ChartSettings from database
    layout, chart_settings, chart_settings_dict, chart_sizes = get_user_dashboard_data(request.user)
    
    available_charts = get_available_charts(request.user, request)
    
    context = {
        "filter_form": filter_form,
        "date_range_form": date_range_form,
        "total_user_overview_responses": total_user_overview_responses,
        "preferences_by_age": preferences_by_age_responses,
        "preferences_by_gender": preferences_by_gender_responses,
        "preferences_per_origin_country": preferences_per_origin_country_responses,
        "preferences_per_destination_country": preferences_per_destination_country_responses,
        "preferences_selected_user_language": preferences_by_language_responses,
        "work_code_usage": preferences_by_organisation_responses,
        "has_orgs": len(get_user_organisations(request.user)) > 0,
        "pasi_downloads": pasi_downloads,
        "pref_cumulative_monthly_new_users": pref_cumulative_new_users,
        "users_by_country_state": users_by_country_state,
        "preferences_by_sectors": preferences_by_sectors,
        "sws_workcodes_with_access_code": sws_workcodes_with_access_code,
        "monthly_active_user_count": monthly_active_users,
        "total_active_user_count": total_active_users,
        "get_user_counts_by_origin_destination": json.dumps(
            list(user_counts_by_origin_destination), cls=DjangoJSONEncoder
        ),
        "get_user_counts_by_geolocation": user_counts_by_geolocation,
        "country_coords": country_coords,
        "preferences_by_immigration_status": preferences_by_immigration_status_responses,
        "link_clicks_data": link_clicks_data,
        "user_counts_by_geo_country": user_counts_by_geo_country,
        "available_charts": available_charts,
        "dashboard_layout": json.dumps(layout, cls=DjangoJSONEncoder),
        "chart_settings": json.dumps(chart_settings, cls=DjangoJSONEncoder),
        "chart_settings_dict": chart_settings_dict, 
        "chart_sizes": chart_sizes,  
    }
    return render(request, "preference/user_overview.html", context=context)

def get_user_dashboard_data(user):
    """
    Get dashboard preferences and chart settings for a user.
    
    Returns:
        tuple: (layout, chart_settings, chart_settings_dict, chart_sizes)
            - layout: Dashboard layout dictionary
            - chart_settings: Chart settings dict with ISO date strings (for JSON)
            - chart_settings_dict: Chart settings dict with date objects (for template)
            - chart_sizes: Simple dict mapping chart_id to size
    """
    try:
        dashboard_prefs = user.dashboard_prefs
        layout = dashboard_prefs.get_layout()
        chart_settings = {}
        chart_settings_dict = {}  
        chart_sizes = {}  
        
        for chart_setting in dashboard_prefs.chart_settings.all():
            chart_settings[chart_setting.chart_id] = {
                'chart_type': chart_setting.chart_type,
                'size': chart_setting.size,
                'enabled': chart_setting.enabled,
                'start_date': chart_setting.start_date.isoformat() if chart_setting.start_date else None,
                'end_date': chart_setting.end_date.isoformat() if chart_setting.end_date else None,
            }
            chart_settings_dict[chart_setting.chart_id] = {
                'chart_type': chart_setting.chart_type,
                'size': chart_setting.size,
                'enabled': chart_setting.enabled,
                'start_date': chart_setting.start_date,
                'end_date': chart_setting.end_date,
            }
            chart_sizes[chart_setting.chart_id] = chart_setting.size
    except DashboardPreferences.DoesNotExist:
        user_prefs = user.dashboard_preferences or {}
        layout = user_prefs.get('layout', {'rows': []})
        chart_settings = user_prefs.get('chart_settings', {})
        chart_settings_dict = chart_settings
        chart_sizes = {k: v.get('size', 6) for k, v in chart_settings.items() if isinstance(v, dict)}
    
    return layout, chart_settings, chart_settings_dict, chart_sizes

@login_required
def user_diagnostics(request):
    preferences = []
    device_id = request.GET.get('device_id', '')
    
    if device_id:
        preferences = get_preferences_by_device_id(device_id)
    
    context = {
        'preferences': preferences,
        'device_id': device_id
    }
    return render(request, 'preference/user_diagnostics.html', context)

def export_preference_stats(request):
    form_filter_params = get_form_filter_params(request=request, form_class=GenericFilterForm)
    filters = form_filter_params["filters"]

    organisations = filters.get("organisations", None)
    if organisations is None:
        user_orgs = get_user_organisations(request.user)
        organisations = [getattr(org, "name") for org in user_orgs]

    export_dict = {
        "all": preference_stats_for_export(
            {**filters, "organisations": organisations, "current_user": request.user}
        )
    }

    for organisation in organisations:
        export_dict[organisation] = preference_stats_for_export(
            {**filters, "organisations": [organisation], "current_user": request.user}
        )
    return generate_and_export_excel(export_dict, "preference_stats")


def export_returning_users_to_excel(request):
    returning_users = get_returning_users_grouped_by_original_device_id()
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Returning Users"

    heading = "Report Showing Details of Returned Users"
    ws.append([])
    ws.append([heading])
    ws.merge_cells(start_row=2, start_column=1, end_row=2, end_column=10)
    heading_cell = ws.cell(row=2, column=1)
    heading_cell.font = Font(size=14, bold=True)
    heading_cell.alignment = Alignment(horizontal="center")
    ws.append([])

    headers = [
        "Original Device ID",
        "ID",
        "Data Source ID",
        "Device ID",
        "Locale",
        "App ID",
        "Cleaned",
        "API Created At",
        "API Updated At",
        "Location of Potential Work",
        "Gender",
        "Age Range",
        "Language",
        "Origin",
        "Destination",
        "API Destination",
        "Destination State",
        "Route",
        "Organisation Sector",
        "Organisation Access Code",
        "Factory Farm",
        "Organisation",
    ]
    ws.append(headers)

    for original_device_id, preferences in returning_users.items():
        ws.append([original_device_id] + [""] * (len(headers) - 1))
        ws.merge_cells(start_row=ws.max_row, start_column=1, end_row=ws.max_row, end_column=len(headers))

        for pref in preferences:
            row = [
                "",
                pref["id"],
                pref["data_source_id"],
                pref["device_id"],
                pref["locale"],
                pref["app_id"],
                pref["cleaned"],
                pref["api_created_at"],
                pref["api_updated_at"],
                pref["location_of_potential_work__name"],
                pref["gender__translated_name"],
                pref["age__range"],
                pref["language__name"],
                pref["origin__name"],
                pref["destination__name"],
                pref["api_destination__name"],
                pref["destination_state__name"],
                pref["route__name"],
                pref["organisation_sector__name"],
                pref["organisation_access_code__code"],
                pref["factory_farm__name"],
                pref["organisation__name"],
            ]
            ws.append(row)

        ws.append([])

    for col_num, col in enumerate(ws.columns, 1):
        max_length = 0
        column = get_column_letter(col_num)
        for cell in col:
            try:
                if len(str(cell.value)) > max_length:
                    max_length = len(cell.value)
            except:
                pass
        adjusted_width = max_length + 2
        ws.column_dimensions[column].width = adjusted_width

    response = HttpResponse(content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    response["Content-Disposition"] = "attachment; filename=returning_users.xlsx"
    wb.save(response)
    return response


def export_help_contacts_data(request):
    form_filter_params = get_form_filter_params(request=request, form_class=GenericFilterForm)
    filters = form_filter_params["filters"]
    start_date = filters.get("start_date")
    end_date = filters.get("end_date")
    inline_data = get_help_contacts_between_dates(**filters, current_user=request.user)

    wb = openpyxl.Workbook()
    ws = wb.active

    if start_date and end_date:
        heading = f"Help Contacts Report for the Period Starting {start_date} to {end_date}"
    else:
        heading = "Help Contacts Report for all time"
    ws.merge_cells(start_row=2, start_column=1, end_row=2, end_column=10)
    heading_cell = ws.cell(row=2, column=1, value=heading)
    heading_cell.alignment = Alignment(horizontal="center", vertical="center")
    heading_cell.font = Font(bold=True)

    headers = [
        "Created At",
        "Device ID",
        "Contact Type",
        "Contact",
        "Origin",
        "Destination",
        "Locale",
    ]

    for idx, header in enumerate(headers, start=1):
        ws.cell(row=4, column=idx, value=header)

    for idx, data in enumerate(inline_data, start=5):
        created_at = data["api_created_at"]
        origin_value = data["origin__name"] if data["origin__name"] else None
        destination_value = data["destination__name"] if data["destination__name"] else None

        ws.cell(row=idx, column=1, value=created_at.strftime("%Y-%m-%d"))
        ws.cell(row=idx, column=2, value=data["device_id"])
        ws.cell(row=idx, column=3, value=data["contact_type"])
        ws.cell(row=idx, column=4, value=data["translated_contact_value"])
        ws.cell(row=idx, column=5, value=origin_value)
        ws.cell(row=idx, column=6, value=destination_value)
        ws.cell(row=idx, column=7, value=data["locale"])

    response = HttpResponse(content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    response["Content-Disposition"] = "attachment; filename=Help_contacts_data.xlsx"

    wb.save(response)

    return response


def export_preferences_data(request):
    form_filter_params = get_form_filter_params(request=request, form_class=GenericFilterForm)
    filters = form_filter_params["filters"]

    preferences_data = extract_preference_for_export(**filters, current_user=request.user)

    wb = openpyxl.Workbook()
    ws = wb.active

    start_date = filters.get("start_date")
    end_date = filters.get("end_date")

    if start_date and end_date:
        heading = f"Preferences Report from {start_date} to {end_date}"
    else:
        heading = "Preferences Report"

    ws.merge_cells(start_row=2, start_column=1, end_row=2, end_column=9)
    heading_cell = ws.cell(row=2, column=1, value=heading)
    heading_cell.alignment = Alignment(horizontal="center", vertical="center")
    heading_cell.font = Font(bold=True)

    is_sws_config = request.user.groups.filter(name="SWSConfig").exists()

    headers = [
        "Data Source ID",
        "Device ID",
        "Locale",
        "App ID",
        "Api Created At",
        "API Updated At",
        "Location of Potential Work",
        "Gender",
        "Age Range",
        "Language",
        "Origin",
        "Destination",
        "Route",
        "Organisation Sector",
    ]

    if not is_sws_config:
        headers.insert(15, "Organisation Access Code")
        headers.append("Organisation")

    for idx, header in enumerate(headers, start=1):
        ws.cell(row=4, column=idx, value=header)

    for idx, data in enumerate(preferences_data, start=5):
        ws.cell(row=idx, column=1, value=data["data_source_id"])
        ws.cell(row=idx, column=2, value=data["device_id"])
        ws.cell(row=idx, column=3, value=data["locale"])
        ws.cell(row=idx, column=4, value=data["app_id"])
        ws.cell(row=idx, column=5, value=data["api_created_at"].strftime("%Y-%m-%d"))
        ws.cell(row=idx, column=6, value=data["api_updated_at"].strftime("%Y-%m-%d"))
        ws.cell(row=idx, column=7, value=data["location_of_potential_work__name"])
        ws.cell(row=idx, column=8, value=data["gender__translated_name"])
        ws.cell(row=idx, column=9, value=data["age__range"])
        ws.cell(row=idx, column=10, value=data["language__name"])
        ws.cell(row=idx, column=11, value=data["origin__name"])
        ws.cell(row=idx, column=12, value=data["destination__name"])
        ws.cell(row=idx, column=13, value=data["route__name"])
        ws.cell(row=idx, column=14, value=", ".join(data["sectors_of_work__translated_name"]))
        if not is_sws_config:
            ws.cell(row=idx, column=15, value=data["organisation_access_code__code"])
            ws.cell(row=idx, column=16, value=data["org_info__name"])

    response = HttpResponse(content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    response["Content-Disposition"] = (
        f'attachment; filename="preferences_report_from_{start_date}_to_{end_date}.xlsx"'
    )
    wb.save(response)

    return response


def export_pay_calculator_statistics(request):
    """Export PayCalculator statistics grouped by origin, Organisation, and Organisation Access Code"""
    form_filter_params = get_form_filter_params(request=request, form_class=GenericFilterForm)
    filters = form_filter_params["filters"]
    start_date = filters.get("start_date")
    end_date = filters.get("end_date")

    statistics_data = get_pay_calculator_statistics(start_date=start_date, end_date=end_date)

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Pay Calculator Statistics"

    heading_text = "Pay Calculator Statistics"
    if start_date and end_date:
        heading_text = f"Pay Calculator Statistics from {start_date} to {end_date}"
    ws.merge_cells(start_row=2, start_column=1, end_row=2, end_column=5)
    heading_cell = ws.cell(row=2, column=1, value=heading_text)
    heading_cell.alignment = Alignment(horizontal="center", vertical="center")
    heading_cell.font = Font(bold=True, size=14)
    
    headers = [
        "Country of Origin",
        "Organisation",
        "Organisation Access Code",
        "Number of Users",
        "Total Records Created",
    ]
    
    for idx, header in enumerate(headers, start=1):
        cell = ws.cell(row=4, column=idx, value=header)
        cell.font = Font(bold=True)
        cell.alignment = Alignment(horizontal="center", vertical="center")
    
    for idx, data in enumerate(statistics_data, start=5):
        ws.cell(row=idx, column=1, value=data.get("origin__name") or "N/A")
        ws.cell(row=idx, column=2, value=data.get("organisation__name") or "N/A")
        ws.cell(row=idx, column=3, value=data.get("organisation_access_code__code") or "N/A")
        ws.cell(row=idx, column=4, value=data.get("unique_device_count", 0))
        ws.cell(row=idx, column=5, value=data.get("total_records", 0))
    
    for col_num, col in enumerate(ws.columns, 1):
        max_length = 0
        column = get_column_letter(col_num)
        for cell in col:
            try:
                if len(str(cell.value)) > max_length:
                    max_length = len(str(cell.value))
            except:
                pass
        adjusted_width = max_length + 2
        ws.column_dimensions[column].width = adjusted_width
    
    total_row = len(statistics_data) + 6
    ws.cell(row=total_row, column=1, value="TOTAL").font = Font(bold=True)
    ws.cell(row=total_row, column=4, value=sum(d.get("unique_device_count", 0) for d in statistics_data)).font = Font(bold=True)
    ws.cell(row=total_row, column=5, value=sum(d.get("total_records", 0) for d in statistics_data)).font = Font(bold=True)
    
    response = HttpResponse(content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    filename = "pay_calculator_statistics.xlsx"
    if start_date and end_date:
        filename = f"pay_calculator_statistics_from_{start_date}_to_{end_date}.xlsx"
    response["Content-Disposition"] = f'attachment; filename="{filename}"'
    wb.save(response)

    return response


def get_available_charts(user, request=None):
    """Get list of chart IDs available to user from ChartSettings database"""
    
    logger = logging.getLogger(__name__)
    available = []
    
    try:
        dashboard_prefs = DashboardPreferences.objects.get(user=user)
        
        chart_settings = ChartSettings.objects.filter(
            dashboard_preferences=dashboard_prefs,
            enabled=True  
        ).values_list('chart_id', flat=True).distinct()
        
        available = list(chart_settings)
        
        logger.info(f"Found {len(available)} charts from ChartSettings for user {user.email}: {available}")
        
    except DashboardPreferences.DoesNotExist:
        logger.info(f"DashboardPreferences not found for user {user.email}, returning empty list")
        return []
    except Exception as e:
        logger.error(f"Error getting available charts from ChartSettings: {str(e)}")
        return []
    
    logger.info(f"Total available charts: {len(available)} - {available}")
    return available


def get_default_dashboard_layout(user, request=None):
    available_charts = get_available_charts(user, request)
    
    if not available_charts:
        return {'rows': []}
    
    default_layout = {'rows': []}
    current_row = {'id': 'row-0', 'columns': []}
    
    for i, chart_id in enumerate(available_charts):
        if len(current_row['columns']) >= 2 and i > 0:
            default_layout['rows'].append(current_row)
            current_row = {'id': f'row-{len(default_layout["rows"])}', 'columns': []}
        
        chart_config = CHART_DEFINITIONS[chart_id]
        col_size = chart_config.get('default_size', 6)
        
        if len(current_row['columns']) == 0 and col_size < 12:
            if i + 1 < len(available_charts):
                next_chart = CHART_DEFINITIONS[available_charts[i + 1]]
                if next_chart.get('default_size', 6) >= 12:
                    col_size = 12
        
        current_row['columns'].append({
            'id': f'col-{chart_id}',
            'chart_id': chart_id,
            'size': col_size,
            'enabled': True,
            'settings': get_default_chart_settings(chart_id)
        })
    
    if current_row['columns']:
        default_layout['rows'].append(current_row)
    
    return default_layout


@login_required
@require_http_methods(["GET", "POST"])
def dashboard_customization(request):
    """Get or save user's dashboard preferences"""
    if request.method == 'GET':
        try:
            dashboard_prefs = request.user.dashboard_prefs
            layout = dashboard_prefs.get_layout()
            chart_settings = {}
            for chart_setting in dashboard_prefs.chart_settings.all():
                chart_settings[chart_setting.chart_id] = {
                    'chart_type': chart_setting.chart_type,
                    'size': chart_setting.size,
                    'enabled': chart_setting.enabled,
                    'start_date': chart_setting.start_date.isoformat() if chart_setting.start_date else None,
                    'end_date': chart_setting.end_date.isoformat() if chart_setting.end_date else None,
                }
        except DashboardPreferences.DoesNotExist:
            preferences = request.user.dashboard_preferences or {}
            layout = preferences.get('layout', get_default_dashboard_layout(request.user, request))
            chart_settings = preferences.get('chart_settings', {})
        
        available_charts = get_available_charts(request.user, request)
        
        logger = logging.getLogger(__name__)
        logger.info(f"Dashboard customization API called. Available charts: {available_charts}")
        
        chart_defs = {}
        for chart_id in available_charts:
            if chart_id in CHART_DEFINITIONS:
                chart_defs[chart_id] = {
                    'name': CHART_DEFINITIONS[chart_id]['name'],
                    'description': CHART_DEFINITIONS[chart_id]['description'],
                    'icon': CHART_DEFINITIONS[chart_id]['icon'],
                    'supported_types': CHART_DEFINITIONS[chart_id]['supported_types'],
                    'default_size': CHART_DEFINITIONS[chart_id]['default_size'],
                    'default_type': CHART_DEFINITIONS[chart_id]['default_type'],
                    'render_function': CHART_DEFINITIONS[chart_id]['render_function'],
                    'data_variable': CHART_DEFINITIONS[chart_id].get('data_variable', '')
                }
        
        logger.info(f"Built {len(chart_defs)} chart definitions for frontend")
        
        return JsonResponse({
            'layout': layout,
            'available_charts': available_charts,
            'chart_definitions': chart_defs,
            'chart_settings': chart_settings  
        })
    
    elif request.method == 'POST':
        try:
            data = json.loads(request.body)
            
            available_charts = get_available_charts(request.user, request)
            
            dashboard_prefs, created = DashboardPreferences.objects.get_or_create(
                user=request.user
            )
            
            if 'layout' in data and 'rows' in data['layout']:
                validated_rows = []
                for row in data['layout']['rows']:
                    if 'columns' in row:
                        validated_columns = []
                        for col in row['columns']:
                            if 'chart_id' in col and col['chart_id'] in available_charts:
                                validated_columns.append(col)
                                
                                chart_id = col['chart_id']
                                settings = col.get('settings', {})
                                
                                chart_setting, _ = ChartSettings.objects.get_or_create(
                                    dashboard_preferences=dashboard_prefs,
                                    chart_id=chart_id,
                                    defaults={
                                        'chart_type': settings.get('chart_type', 'bar'),
                                        'size': col.get('size', 6),
                                        'enabled': col.get('enabled', True),
                                    }
                                )
                                
                                if 'chart_type' in settings:
                                    chart_setting.chart_type = settings['chart_type']
                                if 'size' in col:
                                    chart_setting.size = col['size']
                                if 'enabled' in col:
                                    chart_setting.enabled = col['enabled']
                                if 'start_date' in settings:
                                    from django.utils.dateparse import parse_date
                                    chart_setting.start_date = parse_date(settings['start_date']) if settings['start_date'] else None
                                if 'end_date' in settings:
                                    from django.utils.dateparse import parse_date
                                    chart_setting.end_date = parse_date(settings['end_date']) if settings['end_date'] else None
                                
                                chart_setting.save()
                                
                        if validated_columns:
                            row['columns'] = validated_columns
                            validated_rows.append(row)
                data['layout']['rows'] = validated_rows
                dashboard_prefs.layout = data['layout']
                dashboard_prefs.save()
            
            return JsonResponse({'status': 'success', 'message': 'Dashboard layout saved successfully'})
        except json.JSONDecodeError:
            return JsonResponse({'status': 'error', 'message': 'Invalid JSON data'}, status=400)
        except Exception as e:
            logger = logging.getLogger(__name__)
            logger.error(f'Error saving dashboard: {str(e)}')
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)


@login_required
@require_http_methods(["GET", "POST", "PUT"])
def chart_settings_api(request, chart_id=None):
    """Get or update individual chart settings"""
    try:
        dashboard_prefs, created = DashboardPreferences.objects.get_or_create(
            user=request.user
        )
        
        if request.method == 'GET':
            if chart_id:
                print(f"Chart ID: {chart_id}")
                available_charts = get_available_charts(request.user, request)
                print(f"Available charts: {available_charts}")
                if chart_id not in available_charts:
                    return JsonResponse({
                        'status': 'error',
                        'message': f'Chart {chart_id} is not available for this user'
                    }, status=403)
                
                chart_def = None
                if chart_id in CHART_DEFINITIONS:
                    chart_def = {
                        'name': CHART_DEFINITIONS[chart_id]['name'],
                        'description': CHART_DEFINITIONS[chart_id]['description'],
                        'icon': CHART_DEFINITIONS[chart_id]['icon'],
                        'supported_types': CHART_DEFINITIONS[chart_id]['supported_types'],
                        'default_size': CHART_DEFINITIONS[chart_id]['default_size'],
                        'default_type': CHART_DEFINITIONS[chart_id]['default_type'],
                        'render_function': CHART_DEFINITIONS[chart_id]['render_function'],
                        'data_variable': CHART_DEFINITIONS[chart_id].get('data_variable', '')
                    }
                
                try:
                    chart_setting = ChartSettings.objects.get(
                        dashboard_preferences=dashboard_prefs,
                        chart_id=chart_id
                    )
                    return JsonResponse({
                        'status': 'success',
                        'chart_id': chart_id,
                        'chart_definition': chart_def,
                        'settings': {
                            'chart_type': chart_setting.chart_type,
                            'size': chart_setting.size,
                            'enabled': chart_setting.enabled,
                            'start_date': chart_setting.start_date.isoformat() if chart_setting.start_date else None,
                            'end_date': chart_setting.end_date.isoformat() if chart_setting.end_date else None,
                        }
                    })
                except ChartSettings.DoesNotExist:
                    return JsonResponse({
                        'status': 'success',
                        'chart_id': chart_id,
                        'chart_definition': chart_def,
                        'settings': {
                            'chart_type': chart_def['default_type'] if chart_def else 'bar',
                            'size': chart_def['default_size'] if chart_def else 6,
                            'enabled': True,
                            'start_date': None,
                            'end_date': None,
                        }
                    })
            else:
                chart_settings = {}
                for chart_setting in dashboard_prefs.chart_settings.all():
                    chart_settings[chart_setting.chart_id] = {
                        'chart_type': chart_setting.chart_type,
                        'size': chart_setting.size,
                        'enabled': chart_setting.enabled,
                        'start_date': chart_setting.start_date.isoformat() if chart_setting.start_date else None,
                        'end_date': chart_setting.end_date.isoformat() if chart_setting.end_date else None,
                    }
                return JsonResponse({
                    'status': 'success',
                    'settings': chart_settings
                })
        
        elif request.method in ['POST', 'PUT']:
            if not chart_id:
                return JsonResponse({
                    'status': 'error',
                    'message': 'chart_id is required'
                }, status=400)
            
            data = json.loads(request.body)
            
            available_charts = get_available_charts(request.user, request)
            if chart_id not in available_charts:
                return JsonResponse({
                    'status': 'error',
                    'message': f'Chart {chart_id} is not available for this user'
                }, status=403)
            
            chart_setting, created = ChartSettings.objects.get_or_create(
                dashboard_preferences=dashboard_prefs,
                chart_id=chart_id,
                defaults={
                    'chart_type': data.get('chart_type', 'bar'),
                    'size': data.get('size', 6),
                    'enabled': data.get('enabled', True),
                }
            )
            
            if 'chart_type' in data:
                chart_setting.chart_type = data['chart_type']
            if 'size' in data:
                chart_setting.size = int(data['size'])
            if 'enabled' in data:
                chart_setting.enabled = bool(data['enabled'])
            if 'start_date' in data:
                from django.utils.dateparse import parse_date
                chart_setting.start_date = parse_date(data['start_date']) if data['start_date'] else None
            if 'end_date' in data:
                from django.utils.dateparse import parse_date
                chart_setting.end_date = parse_date(data['end_date']) if data['end_date'] else None
            
            chart_setting.save()
            
            return JsonResponse({
                'status': 'success',
                'message': f'Chart settings {"created" if created else "updated"} successfully',
                'chart_id': chart_id,
                'settings': {
                    'chart_type': chart_setting.chart_type,
                    'size': chart_setting.size,
                    'enabled': chart_setting.enabled,
                    'start_date': chart_setting.start_date.isoformat() if chart_setting.start_date else None,
                    'end_date': chart_setting.end_date.isoformat() if chart_setting.end_date else None,
                }
            })
    
    except json.JSONDecodeError:
        return JsonResponse({'status': 'error', 'message': 'Invalid JSON data'}, status=400)
    except Exception as e:
        logger = logging.getLogger(__name__)
        logger.error(f'Error in chart_settings_api: {str(e)}')
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)


@login_required
@require_http_methods(["POST"])
def reset_dashboard(request):
    """Restore dashboard layout and chart settings to defaults from dashboard_config."""
    try:
        permitted = [
            chart_id
            for chart_id, config in CHART_DEFINITIONS.items()
            if is_flag_active(request, config['waffle_flag'])
        ]
        if not permitted:
            permitted = list(CHART_DEFINITIONS.keys())

        default_prefs = get_default_dashboard_preferences(permitted)

        with transaction.atomic():
            dashboard_prefs, _ = DashboardPreferences.objects.get_or_create(
                user=request.user
            )
            dashboard_prefs.layout = default_prefs['layout']
            dashboard_prefs.chart_definitions = default_prefs['chart_definitions']
            dashboard_prefs.save()

            ChartSettings.objects.filter(dashboard_preferences=dashboard_prefs).delete()

            to_create = [
                ChartSettings(
                    dashboard_preferences=dashboard_prefs,
                    chart_id=chart_id,
                    chart_type=CHART_DEFINITIONS[chart_id]['default_type'],
                    size=CHART_DEFINITIONS[chart_id]['default_size'],
                    enabled=True,
                    start_date=None,
                    end_date=None,
                )
                for chart_id in permitted
                if chart_id in CHART_DEFINITIONS
            ]
            if to_create:
                ChartSettings.objects.bulk_create(to_create)

            chart_settings_json = {
                chart_id: {
                    'chart_type': CHART_DEFINITIONS[chart_id]['default_type'],
                    'size': CHART_DEFINITIONS[chart_id]['default_size'],
                    'enabled': True,
                    'start_date': None,
                    'end_date': None,
                }
                for chart_id in permitted
                if chart_id in CHART_DEFINITIONS
            }
            request.user.dashboard_preferences = {
                'layout': default_prefs['layout'],
                'chart_settings': chart_settings_json,
                'chart_definitions': default_prefs['chart_definitions'],
            }
            request.user.save(update_fields=['dashboard_preferences'])

        return JsonResponse({'status': 'success', 'message': 'Dashboard reset to default'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)


@login_required
@require_http_methods(["POST"])
def filter_monthly_active_users(request):
    """Return monthly active user data for provided date range"""
    logger = logging.getLogger(__name__)
    
    try:
        payload = json.loads(request.body.decode('utf-8'))
    except (json.JSONDecodeError, UnicodeDecodeError):
        return JsonResponse({'status': 'error', 'message': 'Invalid JSON payload'}, status=400)
    
    start_date = payload.get('start_date')
    end_date = payload.get('end_date')
    
    if not start_date or not end_date:
        return JsonResponse(
            {'status': 'error', 'message': 'start_date and end_date are required'},
            status=400
        )
    
    try:
        datetime.strptime(start_date, "%Y-%m-%d")
        datetime.strptime(end_date, "%Y-%m-%d")
    except ValueError:
        return JsonResponse(
            {'status': 'error', 'message': 'Dates must be in YYYY-MM-DD format'},
            status=400
        )
    
    try:
        results = get_monthly_active_user_count(
            start_date=start_date,
            end_date=end_date,
            current_user=request.user
        )
        serialized_results = json.loads(json.dumps(results, cls=DjangoJSONEncoder))
        
        return JsonResponse({
            'status': 'success',
            'data': serialized_results,
            'metadata': {
                'start_date': start_date,
                'end_date': end_date
            }
        })
    except Exception as exc:
        logger = logging.getLogger(__name__)
        logger.error("Error filtering monthly active users: %s", exc, exc_info=True)
        return JsonResponse(
            {'status': 'error', 'message': 'Unable to fetch data for the selected range'},
            status=500
        )


@login_required
@require_http_methods(["POST"])
def filter_users_by_origin(request):
    """Return users by origin country data for provided date range"""
    logger = logging.getLogger(__name__)
    
    try:
        payload = json.loads(request.body.decode('utf-8'))
    except (json.JSONDecodeError, UnicodeDecodeError):
        return JsonResponse({'status': 'error', 'message': 'Invalid JSON payload'}, status=400)
    
    start_date = payload.get('start_date')
    end_date = payload.get('end_date')
    
    if not start_date or not end_date:
        return JsonResponse(
            {'status': 'error', 'message': 'start_date and end_date are required'},
            status=400
        )
    
    try:
        datetime.strptime(start_date, "%Y-%m-%d")
        datetime.strptime(end_date, "%Y-%m-%d")
    except ValueError:
        return JsonResponse(
            {'status': 'error', 'message': 'Dates must be in YYYY-MM-DD format'},
            status=400
        )
    
    try:
        filters = {
            'start_date': start_date,
            'end_date': end_date
        }
        results = preferences_by_origin(**filters, current_user=request.user)
        serialized_results = json.loads(json.dumps(results, cls=DjangoJSONEncoder))
        
        return JsonResponse({
            'status': 'success',
            'data': serialized_results,
            'metadata': {
                'start_date': start_date,
                'end_date': end_date
            }
        })
    except Exception as exc:
        logger.error("Error filtering users by origin: %s", exc, exc_info=True)
        return JsonResponse(
            {'status': 'error', 'message': 'Unable to fetch data for the selected range'},
            status=500
        )


@login_required
@require_http_methods(["POST"])
def filter_users_by_gender(request):
    """Return users by gender data for provided date range"""
    logger = logging.getLogger(__name__)
    
    try:
        payload = json.loads(request.body.decode('utf-8'))
    except (json.JSONDecodeError, UnicodeDecodeError):
        return JsonResponse({'status': 'error', 'message': 'Invalid JSON payload'}, status=400)
    
    start_date = payload.get('start_date')
    end_date = payload.get('end_date')
    
    if not start_date or not end_date:
        return JsonResponse(
            {'status': 'error', 'message': 'start_date and end_date are required'},
            status=400
        )
    
    try:
        datetime.strptime(start_date, "%Y-%m-%d")
        datetime.strptime(end_date, "%Y-%m-%d")
    except ValueError:
        return JsonResponse(
            {'status': 'error', 'message': 'Dates must be in YYYY-MM-DD format'},
            status=400
        )
    
    try:
        filters = {
            'start_date': start_date,
            'end_date': end_date
        }
        results = preferences_by_gender(**filters, current_user=request.user)
        serialized_results = json.loads(json.dumps(results, cls=DjangoJSONEncoder))
        
        return JsonResponse({
            'status': 'success',
            'data': serialized_results,
            'metadata': {
                'start_date': start_date,
                'end_date': end_date
            }
        })
    except Exception as exc:
        logger.error("Error filtering users by gender: %s", exc, exc_info=True)
        return JsonResponse(
            {'status': 'error', 'message': 'Unable to fetch data for the selected range'},
            status=500
        )


@login_required
@require_http_methods(["POST"])
def filter_users_by_destination(request):
    """Return users by destination country data for provided date range"""
    logger = logging.getLogger(__name__)
    
    try:
        payload = json.loads(request.body.decode('utf-8'))
    except (json.JSONDecodeError, UnicodeDecodeError):
        return JsonResponse({'status': 'error', 'message': 'Invalid JSON payload'}, status=400)
    
    start_date = payload.get('start_date')
    end_date = payload.get('end_date')
    
    if not start_date or not end_date:
        return JsonResponse(
            {'status': 'error', 'message': 'start_date and end_date are required'},
            status=400
        )
    
    try:
        datetime.strptime(start_date, "%Y-%m-%d")
        datetime.strptime(end_date, "%Y-%m-%d")
    except ValueError:
        return JsonResponse(
            {'status': 'error', 'message': 'Dates must be in YYYY-MM-DD format'},
            status=400
        )
    
    try:
        filters = {
            'start_date': start_date,
            'end_date': end_date
        }
        results = preferences_by_destination(**filters, current_user=request.user)
        serialized_results = json.loads(json.dumps(results, cls=DjangoJSONEncoder))
        
        return JsonResponse({
            'status': 'success',
            'data': serialized_results,
            'metadata': {
                'start_date': start_date,
                'end_date': end_date
            }
        })
    except Exception as exc:
        logger.error("Error filtering users by destination: %s", exc, exc_info=True)
        return JsonResponse(
            {'status': 'error', 'message': 'Unable to fetch data for the selected range'},
            status=500
        )


@login_required
@require_http_methods(["POST"])
def filter_users_by_language(request):
    """Return users by language data for provided date range"""
    logger = logging.getLogger(__name__)
    
    try:
        payload = json.loads(request.body.decode('utf-8'))
    except (json.JSONDecodeError, UnicodeDecodeError):
        return JsonResponse({'status': 'error', 'message': 'Invalid JSON payload'}, status=400)
    
    start_date = payload.get('start_date')
    end_date = payload.get('end_date')
    
    if not start_date or not end_date:
        return JsonResponse(
            {'status': 'error', 'message': 'start_date and end_date are required'},
            status=400
        )
    
    try:
        datetime.strptime(start_date, "%Y-%m-%d")
        datetime.strptime(end_date, "%Y-%m-%d")
    except ValueError:
        return JsonResponse(
            {'status': 'error', 'message': 'Dates must be in YYYY-MM-DD format'},
            status=400
        )
    
    try:
        filters = {
            'start_date': start_date,
            'end_date': end_date
        }
        results = preferences_by_language(**filters, current_user=request.user)
        serialized_results = json.loads(json.dumps(results, cls=DjangoJSONEncoder))
        
        return JsonResponse({
            'status': 'success',
            'data': serialized_results,
            'metadata': {
                'start_date': start_date,
                'end_date': end_date
            }
        })
    except Exception as exc:
        logger.error("Error filtering users by language: %s", exc, exc_info=True)
        return JsonResponse(
            {'status': 'error', 'message': 'Unable to fetch data for the selected range'},
            status=500
        )


@login_required
@require_http_methods(["POST"])
def filter_users_by_state(request):
    """Return users by state data for provided date range"""
    logger = logging.getLogger(__name__)
    
    try:
        payload = json.loads(request.body.decode('utf-8'))
    except (json.JSONDecodeError, UnicodeDecodeError):
        return JsonResponse({'status': 'error', 'message': 'Invalid JSON payload'}, status=400)
    
    start_date = payload.get('start_date')
    end_date = payload.get('end_date')
    
    if not start_date or not end_date:
        return JsonResponse(
            {'status': 'error', 'message': 'start_date and end_date are required'},
            status=400
        )
    
    try:
        datetime.strptime(start_date, "%Y-%m-%d")
        datetime.strptime(end_date, "%Y-%m-%d")
    except ValueError:
        return JsonResponse(
            {'status': 'error', 'message': 'Dates must be in YYYY-MM-DD format'},
            status=400
        )
    
    try:
        filters = {
            'start_date': start_date,
            'end_date': end_date
        }
        results = get_users_by_country_state(**filters, current_user=request.user)
        serialized_results = json.loads(json.dumps(results, cls=DjangoJSONEncoder))
        
        return JsonResponse({
            'status': 'success',
            'data': serialized_results,
            'metadata': {
                'start_date': start_date,
                'end_date': end_date
            }
        })
    except Exception as exc:
        logger.error("Error filtering users by state: %s", exc, exc_info=True)
        return JsonResponse(
            {'status': 'error', 'message': 'Unable to fetch data for the selected range'},
            status=500
        )


@login_required
@require_http_methods(["POST"])
def filter_users_by_immigration(request):
    """Return users by immigration status data for provided date range"""
    logger = logging.getLogger(__name__)
    
    try:
        payload = json.loads(request.body.decode('utf-8'))
    except (json.JSONDecodeError, UnicodeDecodeError):
        return JsonResponse({'status': 'error', 'message': 'Invalid JSON payload'}, status=400)
    
    start_date = payload.get('start_date')
    end_date = payload.get('end_date')
    
    if not start_date or not end_date:
        return JsonResponse(
            {'status': 'error', 'message': 'start_date and end_date are required'},
            status=400
        )
    
    try:
        datetime.strptime(start_date, "%Y-%m-%d")
        datetime.strptime(end_date, "%Y-%m-%d")
    except ValueError:
        return JsonResponse(
            {'status': 'error', 'message': 'Dates must be in YYYY-MM-DD format'},
            status=400
        )
    
    try:
        filters = {
            'start_date': start_date,
            'end_date': end_date
        }
        results = preferences_by_immigration_status(**filters, current_user=request.user)
        serialized_results = json.loads(json.dumps(results, cls=DjangoJSONEncoder))
        
        return JsonResponse({
            'status': 'success',
            'data': serialized_results,
            'metadata': {
                'start_date': start_date,
                'end_date': end_date
            }
        })
    except Exception as exc:
        logger.error("Error filtering users by immigration status: %s", exc, exc_info=True)
        return JsonResponse(
            {'status': 'error', 'message': 'Unable to fetch data for the selected range'},
            status=500
        )


@login_required
@require_http_methods(["POST"])
def filter_users_by_age(request):
    """Return users by age data for provided date range"""
    logger = logging.getLogger(__name__)
    
    try:
        payload = json.loads(request.body.decode('utf-8'))
    except (json.JSONDecodeError, UnicodeDecodeError):
        return JsonResponse({'status': 'error', 'message': 'Invalid JSON payload'}, status=400)
    
    start_date = payload.get('start_date')
    end_date = payload.get('end_date')
    
    if not start_date or not end_date:
        return JsonResponse(
            {'status': 'error', 'message': 'start_date and end_date are required'},
            status=400
        )
    
    try:
        datetime.strptime(start_date, "%Y-%m-%d")
        datetime.strptime(end_date, "%Y-%m-%d")
    except ValueError:
        return JsonResponse(
            {'status': 'error', 'message': 'Dates must be in YYYY-MM-DD format'},
            status=400
        )
    
    try:
        filters = {
            'start_date': start_date,
            'end_date': end_date
        }
        results = preferences_by_age(**filters, current_user=request.user)
        serialized_results = json.loads(json.dumps(results, cls=DjangoJSONEncoder))
        
        return JsonResponse({
            'status': 'success',
            'data': serialized_results,
            'metadata': {
                'start_date': start_date,
                'end_date': end_date
            }
        })
    except Exception as exc:
        logger.error("Error filtering users by age: %s", exc, exc_info=True)
        return JsonResponse(
            {'status': 'error', 'message': 'Unable to fetch data for the selected range'},
            status=500
        )


@login_required
@require_http_methods(["POST"])
def filter_users_by_sector(request):
    """Return users by sector data for provided date range"""
    logger = logging.getLogger(__name__)
    
    try:
        payload = json.loads(request.body.decode('utf-8'))
    except (json.JSONDecodeError, UnicodeDecodeError):
        return JsonResponse({'status': 'error', 'message': 'Invalid JSON payload'}, status=400)
    
    start_date = payload.get('start_date')
    end_date = payload.get('end_date')
    
    if not start_date or not end_date:
        return JsonResponse(
            {'status': 'error', 'message': 'start_date and end_date are required'},
            status=400
        )
    
    try:
        datetime.strptime(start_date, "%Y-%m-%d")
        datetime.strptime(end_date, "%Y-%m-%d")
    except ValueError:
        return JsonResponse(
            {'status': 'error', 'message': 'Dates must be in YYYY-MM-DD format'},
            status=400
        )
    
    try:
        filters = {
            'start_date': start_date,
            'end_date': end_date
        }
        results = get_preferences_by_sectors(**filters, current_user=request.user)
        serialized_results = json.loads(json.dumps(results, cls=DjangoJSONEncoder))
        
        return JsonResponse({
            'status': 'success',
            'data': serialized_results,
            'metadata': {
                'start_date': start_date,
                'end_date': end_date
            }
        })
    except Exception as exc:
        logger.error("Error filtering users by sector: %s", exc, exc_info=True)
        return JsonResponse(
            {'status': 'error', 'message': 'Unable to fetch data for the selected range'},
            status=500
        )


@login_required
@require_http_methods(["POST"])
def filter_work_code_usage(request):
    """Return work code usage data for provided date range"""
    logger = logging.getLogger(__name__)
    
    try:
        payload = json.loads(request.body.decode('utf-8'))
    except (json.JSONDecodeError, UnicodeDecodeError):
        return JsonResponse({'status': 'error', 'message': 'Invalid JSON payload'}, status=400)
    
    start_date = payload.get('start_date')
    end_date = payload.get('end_date')
    
    if not start_date or not end_date:
        return JsonResponse(
            {'status': 'error', 'message': 'start_date and end_date are required'},
            status=400
        )
    
    try:
        datetime.strptime(start_date, "%Y-%m-%d")
        datetime.strptime(end_date, "%Y-%m-%d")
    except ValueError:
        return JsonResponse(
            {'status': 'error', 'message': 'Dates must be in YYYY-MM-DD format'},
            status=400
        )
    
    try:
        filters = {
            'start_date': start_date,
            'end_date': end_date
        }
        results = get_sws_workcodes_with_access_code(**filters, current_user=request.user)
        serialized_results = json.loads(json.dumps(results, cls=DjangoJSONEncoder))
        
        return JsonResponse({
            'status': 'success',
            'data': serialized_results,
            'metadata': {
                'start_date': start_date,
                'end_date': end_date
            }
        })
    except Exception as exc:
        logger.error("Error filtering work code usage: %s", exc, exc_info=True)
        return JsonResponse(
            {'status': 'error', 'message': 'Unable to fetch data for the selected range'},
            status=500
        )


@login_required
@require_http_methods(["POST"])
def filter_new_users_by_month(request):
    """Return new monthly users data for provided date range"""
    logger = logging.getLogger(__name__)
    
    try:
        payload = json.loads(request.body.decode('utf-8'))
    except (json.JSONDecodeError, UnicodeDecodeError):
        return JsonResponse({'status': 'error', 'message': 'Invalid JSON payload'}, status=400)
    
    start_date = payload.get('start_date')
    end_date = payload.get('end_date')
    
    if not start_date or not end_date:
        return JsonResponse(
            {'status': 'error', 'message': 'start_date and end_date are required'},
            status=400
        )
    
    try:
        datetime.strptime(start_date, "%Y-%m-%d")
        datetime.strptime(end_date, "%Y-%m-%d")
    except ValueError:
        return JsonResponse(
            {'status': 'error', 'message': 'Dates must be in YYYY-MM-DD format'},
            status=400
        )
    
    try:
        filters = {
            'start_date': start_date,
            'end_date': end_date
        }
        results = get_cumulative_monthly_new_users(**filters, current_user=request.user)
        serialized_results = json.loads(json.dumps(results, cls=DjangoJSONEncoder))
        
        return JsonResponse({
            'status': 'success',
            'data': serialized_results,
            'metadata': {
                'start_date': start_date,
                'end_date': end_date
            }
        })
    except Exception as exc:
        logger.error("Error filtering new users by month: %s", exc, exc_info=True)
        return JsonResponse(
            {'status': 'error', 'message': 'Unable to fetch data for the selected range'},
            status=500
        )

