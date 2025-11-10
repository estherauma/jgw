import json
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
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from preference.dashboard_config import CHART_DEFINITIONS, get_default_chart_settings
import logging


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

    user_prefs = request.user.dashboard_preferences or {}
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
        "dashboard_layout": json.dumps(user_prefs.get('layout', {}), cls=DjangoJSONEncoder),
    }
    return render(request, "preference/user_overview.html", context=context)


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


def get_available_charts(user, request=None):
    """Get list of chart IDs available to user based on waffle flags"""
    from waffle import flag_is_active
    from waffle.models import Flag
    import logging
    
    logger = logging.getLogger(__name__)
    available = []
    
    logger.info(f"Checking available charts for user. Total CHART_DEFINITIONS: {len(CHART_DEFINITIONS)}")
    
    for chart_id, config in CHART_DEFINITIONS.items():
        flag_name = config['waffle_flag']
        is_active = False
        
        if request:
            try:
                is_active = flag_is_active(flag_name, request)
                logger.debug(f"Flag {flag_name} (chart: {chart_id}) - flag_is_active result: {is_active}")
            except Exception as e:
                logger.warning(f"Error checking flag {flag_name} with flag_is_active: {e}")
                try:
                    flag = Flag.objects.filter(name=flag_name).first()
                    if flag:
                        is_active = flag.is_active(request=request)
                        logger.debug(f"Flag {flag_name} (chart: {chart_id}) - database flag.is_active result: {is_active}")
                    else:
                        logger.warning(f"Flag {flag_name} not found in database")
                        is_active = False
                except Exception as ex:
                    logger.error(f"Error checking flag {flag_name} from database: {ex}")
                    is_active = False
        else:
            try:
                flag = Flag.objects.filter(name=flag_name).first()
                if flag:
                    is_active = flag.is_active(request=request)
                    logger.debug(f"Flag {flag_name} (chart: {chart_id}) - database flag.is_active (no request) result: {is_active}")
                else:
                    logger.warning(f"Flag {flag_name} not found in database (no request)")
                    is_active = False
            except Exception as ex:
                logger.error(f"Error checking flag {flag_name} from database (no request): {ex}")
                is_active = False
        
        if is_active:
            available.append(chart_id)
            logger.info(f"✓ Chart {chart_id} is available (flag: {flag_name})")
        else:
            logger.debug(f"✗ Chart {chart_id} is NOT available (flag: {flag_name})")
    
    logger.info(f"Total available charts: {len(available)} - {available}")
    return available


def get_default_dashboard_layout(user, request=None):
    """Generate default layout based on user's waffle flags"""
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
        preferences = request.user.dashboard_preferences or {}
        default_layout = get_default_dashboard_layout(request.user, request)
        
        layout = preferences.get('layout', default_layout)
        available_charts = get_available_charts(request.user, request)
        
        logger = logging.getLogger(__name__)
        logger.info(f"Dashboard customization API called. Available charts: {available_charts}")
        logger.info(f"Total CHART_DEFINITIONS in config: {len(CHART_DEFINITIONS)}")
        
        if not available_charts or len(available_charts) == 0:
            logger.warning("No charts available via flags, returning ALL chart definitions as fallback")
            available_charts = list(CHART_DEFINITIONS.keys())
        
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
            else:
                logger.warning(f"Chart ID {chart_id} not found in CHART_DEFINITIONS")
        
        logger.info(f"Built {len(chart_defs)} chart definitions for frontend")
        
        return JsonResponse({
            'layout': layout,
            'available_charts': available_charts,
            'chart_definitions': chart_defs,
            'user_preferences': preferences
        })
    
    elif request.method == 'POST':
        try:
            data = json.loads(request.body)
            
            available_charts = get_available_charts(request.user, request)
            
            if 'layout' in data and 'rows' in data['layout']:
                validated_rows = []
                for row in data['layout']['rows']:
                    if 'columns' in row:
                        validated_columns = []
                        for col in row['columns']:
                            if 'chart_id' in col and col['chart_id'] in available_charts:
                                validated_columns.append(col)
                        if validated_columns:
                            row['columns'] = validated_columns
                            validated_rows.append(row)
                data['layout']['rows'] = validated_rows
            
            request.user.dashboard_preferences = data
            request.user.save()
            return JsonResponse({'status': 'success', 'message': 'Dashboard layout saved successfully'})
        except json.JSONDecodeError:
            return JsonResponse({'status': 'error', 'message': 'Invalid JSON data'}, status=400)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)


@login_required
@require_http_methods(["POST"])
def reset_dashboard(request):
    """Reset dashboard to default layout"""
    try:
        request.user.dashboard_preferences = {}
        request.user.save()
        return JsonResponse({'status': 'success', 'message': 'Dashboard reset to default'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)


