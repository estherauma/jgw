"""
Dashboard Chart Configuration
Defines all available charts with their metadata, waffle flags, and rendering functions
"""

CHART_DEFINITIONS = {
    'monthly_active_users': {
        'name': 'Monthly Active Users',
        'description': 'Shows monthly active user trends',
        'icon': 'fe-trending-up',
        'supported_types': ['bar', 'pie', 'doughnut'],
        'waffle_flag': 'can_view_monthly_active_users_chart',
        'default_size': 6,
        'default_type': 'bar',
        'render_function': 'initMonthlyActiveUsersChart',
        'data_variable': 'monthlyActiveUserCountData'
    },
    'users_by_origin_country': {
        'name': 'Users by Origin Country',
        'description': 'Distribution of users by country of origin',
        'icon': 'fe-globe',
        'supported_types': ['bar', 'pie', 'doughnut'],
        'waffle_flag': 'can_view_users_by_origin_country_chart',
        'default_size': 6,
        'default_type': 'bar',
        'render_function': 'initUsersByOriginChart',
        'data_variable': 'originData'
    },
    'users_by_gender': {
        'name': 'Users by Gender',
        'description': 'Distribution of users by gender',
        'icon': 'fe-users',
        'supported_types': ['pie', 'doughnut', 'bar'],
        'waffle_flag': 'can_view_users_by_gender_chart',
        'default_size': 6,
        'default_type': 'pie',
        'render_function': 'initUsersByGenderChart',
        'data_variable': 'genderData'
    },
    'users_by_destination_country': {
        'name': 'Users by Destination Country',
        'description': 'Distribution of users by destination country',
        'icon': 'fe-map',
        'supported_types': ['pie', 'doughnut', 'bar'],
        'waffle_flag': 'can_view_users_by_destination_country_chart',
        'default_size': 6,
        'default_type': 'doughnut',
        'render_function': 'initUsersByDestinationChart',
        'data_variable': 'destinationData'
    },
    'users_by_language': {
        'name': 'Users by Language',
        'description': 'Distribution of users by selected language',
        'icon': 'fe-globe',
        'supported_types': ['bar', 'pie', 'doughnut'],
        'waffle_flag': 'can_view_selected_users_language_chart',
        'default_size': 6,
        'default_type': 'bar',
        'render_function': 'initUsersByLanguageChart',
        'data_variable': 'languageData'
    },
    'users_by_country_state': {
        'name': 'Users by Country State',
        'description': 'Distribution of users by country state',
        'icon': 'fe-map-pin',
        'supported_types': ['bar', 'pie', 'doughnut'],
        'waffle_flag': 'can_view_get_users_by_country_state_chart',
        'default_size': 6,
        'default_type': 'bar',
        'render_function': 'initUsersByStateChart',
        'data_variable': 'usersByCountryStateChartData'
    },
    'users_by_immigration_status': {
        'name': 'Users by Immigration Status',
        'description': 'Distribution of users by immigration status',
        'icon': 'fe-file-text',
        'supported_types': ['pie', 'doughnut', 'bar'],
        'waffle_flag': 'can_view_users_by_immigration_status_chart',
        'default_size': 6,
        'default_type': 'bar',
        'render_function': 'initUsersByImmigrationStatusChart',
        'data_variable': 'immigrationStatusData'
    },
    'users_by_age': {
        'name': 'Users by Age',
        'description': 'Distribution of users by age group',
        'icon': 'fe-user',
        'supported_types': ['pie', 'doughnut', 'bar'],
        'waffle_flag': 'can_view_users_by_age_chart',
        'default_size': 6,
        'default_type': 'pie',
        'render_function': 'initUsersByAgeChart',
        'data_variable': 'ageData'
    },
    'users_by_sector': {
        'name': 'Users by Sector',
        'description': 'Distribution of users by work sector',
        'icon': 'fe-briefcase',
        'supported_types': ['bar', 'pie', 'doughnut'],
        'waffle_flag': 'can_view_get_users_by_sector_chart',
        'default_size': 6,
        'default_type': 'bar',
        'render_function': 'initUsersBySectorChart',
        'data_variable': 'usersBySectorsChartData'
    },
    'work_code_usage': {
        'name': 'Work Code Usage',
        'description': 'Work code usage statistics',
        'icon': 'fe-activity',
        'supported_types': ['bar'],
        'waffle_flag': 'can_view_work_code_usage_chart',
        'default_size': 6,
        'default_type': 'bar',
        'render_function': 'initWorkCodeUsageChart',
        'data_variable': 'swsWorkcodesWithAccessCode'
    },
    'new_monthly_users': {
        'name': 'New Monthly Users',
        'description': 'New and cumulative monthly users',
        'icon': 'fe-trending-up',
        'supported_types': ['line', 'bar', 'area'],
        'waffle_flag': 'can_view_new_monthly_users_chart',
        'default_size': 12,
        'default_type': 'line',
        'render_function': 'initPreferencesMonthlyUsersChart',
        'data_variable': 'preferenceMonthlyUsersChartData'
    },
    'link_clicks': {
        'name': 'Link Clicks',
        'description': 'Link click statistics by users',
        'icon': 'fe-mouse-pointer',
        'supported_types': ['bar'],
        'waffle_flag': 'can_view_link_clicks_chart',
        'default_size': 12,
        'default_type': 'bar',
        'render_function': 'linkClicksGraph',
        'data_variable': 'linkClicksData'
    },
    'user_route_map': {
        'name': 'User Route Map',
        'description': 'Visual map of user routes',
        'icon': 'fe-map',
        'supported_types': ['map'],
        'waffle_flag': 'can_view_user_route_map_chart',
        'default_size': 12,
        'default_type': 'map',
        'render_function': 'createUserRouteMap',
        'data_variable': 'getUserCountsByOriginDestination'
    },
    'user_geolocation_map': {
        'name': 'User Geolocation Map',
        'description': 'Visual map of user geolocations',
        'icon': 'fe-map',
        'supported_types': ['map'],
        'waffle_flag': 'can_view_user_geolocation_map',
        'default_size': 12,
        'default_type': 'map',
        'render_function': 'createUserGeolocationMap',
        'data_variable': 'userGeoCountryData'
    },
    'user_geolocation_map_user_engagement': {
        'name': 'User Geolocation Map (Engagement)',
        'description': 'Visual map of user geolocations for engagement',
        'icon': 'fe-map',
        'supported_types': ['map'],
        'waffle_flag': 'can_view_user_geolocation_map_chart_on_user_engagement',
        'default_size': 12,
        'default_type': 'map',
        'render_function': 'createUserGeolocationMap',
        'data_variable': 'getUserCountsByGeolocation'
    }
}
CHART_FLAG_MAP = {chart_id: config['waffle_flag'] for chart_id, config in CHART_DEFINITIONS.items()}

def get_default_chart_settings(chart_id):
    """Get default settings for a chart"""
    if chart_id not in CHART_DEFINITIONS:
        return {}
    
    config = CHART_DEFINITIONS[chart_id]
    return {
        'chart_type': config['default_type'],
        'height': '500px',
        'show_legend': True,
        'show_grid': True,
        'responsive': True
    }


def get_default_dashboard_preferences(available_charts):
    """Get default dashboard preferences (layout and chart_definitions) for given charts"""
    if not available_charts:
        return {
            'layout': {'rows': []},
            'chart_definitions': {}
        }
    
    default_layout = {'rows': []}
    current_row = {'id': 'row-0', 'columns': []}
    
    for i, chart_id in enumerate(available_charts):
        if len(current_row['columns']) >= 2 and i > 0:
            default_layout['rows'].append(current_row)
            current_row = {'id': f'row-{len(default_layout["rows"])}', 'columns': []}
        
        chart_config = CHART_DEFINITIONS.get(chart_id, {})
        col_size = chart_config.get('default_size', 6)
        
        if len(current_row['columns']) == 0 and col_size < 12:
            if i + 1 < len(available_charts):
                next_chart = CHART_DEFINITIONS.get(available_charts[i + 1], {})
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
    
    return {
        'layout': default_layout,
        'chart_definitions': chart_defs
    }

