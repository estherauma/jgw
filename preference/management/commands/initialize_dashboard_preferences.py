from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from datetime import datetime, date
from preference.dashboard_config import get_default_dashboard_preferences, CHART_DEFINITIONS
from preference.models import DashboardPreferences, ChartSettings
from preference.views import get_available_charts

User = get_user_model()


class Command(BaseCommand):
    help = 'Initialize dashboard preferences with CHART_DEFINITIONS for all users'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force re-initialization even if preferences already exist',
        )
        parser.add_argument(
            '--migrate-from-json',
            action='store_true',
            help='Migrate existing JSONField preferences to DashboardPreferences model',
        )

    def handle(self, *args, **options):
        force = options.get('force', False)
        migrate_from_json = options.get('migrate_from_json', False)
        users = User.objects.all()
        total_users = users.count()
        initialized_count = 0
        migrated_count = 0
        skipped_count = 0
        error_count = 0

        self.stdout.write(f'Processing {total_users} users...')

        for user in users:
            try:
                if migrate_from_json and user.dashboard_preferences:
                    user_prefs_json = user.dashboard_preferences
                    
                    filter_start_date = None
                    filter_end_date = None
                    if isinstance(user_prefs_json, dict):
                        if 'filter_start_date' in user_prefs_json and user_prefs_json['filter_start_date']:
                            try:
                                if isinstance(user_prefs_json['filter_start_date'], str):
                                    filter_start_date = datetime.strptime(user_prefs_json['filter_start_date'], '%Y-%m-%d').date()
                                elif isinstance(user_prefs_json['filter_start_date'], date):
                                    filter_start_date = user_prefs_json['filter_start_date']
                            except (ValueError, TypeError) as e:
                                self.stdout.write(self.style.WARNING(f'Could not parse filter_start_date for {user.email}: {e}'))
                        
                        if 'filter_end_date' in user_prefs_json and user_prefs_json['filter_end_date']:
                            try:
                                if isinstance(user_prefs_json['filter_end_date'], str):
                                    filter_end_date = datetime.strptime(user_prefs_json['filter_end_date'], '%Y-%m-%d').date()
                                elif isinstance(user_prefs_json['filter_end_date'], date):
                                    filter_end_date = user_prefs_json['filter_end_date']
                            except (ValueError, TypeError) as e:
                                self.stdout.write(self.style.WARNING(f'Could not parse filter_end_date for {user.email}: {e}'))
                    
                    dashboard_prefs, created = DashboardPreferences.objects.get_or_create(
                        user=user,
                        defaults={
                            'layout': user_prefs_json.get('layout', {'rows': []}) if isinstance(user_prefs_json, dict) else {'rows': []},
                            'chart_definitions': user_prefs_json.get('chart_definitions', {}) if isinstance(user_prefs_json, dict) else {},
                            'filter_start_date': filter_start_date,
                            'filter_end_date': filter_end_date
                        }
                    )
                    
                    chart_settings_json = user_prefs_json.get('chart_settings', {}) if isinstance(user_prefs_json, dict) else {}
                    for chart_id, settings in chart_settings_json.items():
                        chart_start_date = None
                        chart_end_date = None
                        if isinstance(settings, dict):
                            if 'start_date' in settings and settings['start_date']:
                                try:
                                    if isinstance(settings['start_date'], str):
                                        chart_start_date = datetime.strptime(settings['start_date'], '%Y-%m-%d').date()
                                    elif isinstance(settings['start_date'], date):
                                        chart_start_date = settings['start_date']
                                except (ValueError, TypeError):
                                    pass
                            if 'end_date' in settings and settings['end_date']:
                                try:
                                    if isinstance(settings['end_date'], str):
                                        chart_end_date = datetime.strptime(settings['end_date'], '%Y-%m-%d').date()
                                    elif isinstance(settings['end_date'], date):
                                        chart_end_date = settings['end_date']
                                except (ValueError, TypeError):
                                    pass
                        
                        ChartSettings.objects.get_or_create(
                            dashboard_preferences=dashboard_prefs,
                            chart_id=chart_id,
                            defaults={
                                'chart_type': settings.get('chart_type', CHART_DEFINITIONS.get(chart_id, {}).get('default_type', 'bar')) if isinstance(settings, dict) else 'bar',
                                'size': settings.get('size', CHART_DEFINITIONS.get(chart_id, {}).get('default_size', 6)) if isinstance(settings, dict) else 6,
                                'enabled': settings.get('enabled', True) if isinstance(settings, dict) else True,
                                'start_date': chart_start_date,
                                'end_date': chart_end_date
                            }
                        )
                    
                    if created:
                        migrated_count += 1
                        self.stdout.write(f'Migrated preferences for {user.email}')
                    continue

                if not force and DashboardPreferences.objects.filter(user=user).exists():
                    skipped_count += 1
                    continue

                class MockRequest:
                    def __init__(self, user):
                        self.user = user

                mock_request = MockRequest(user)
                available_charts = get_available_charts(user, mock_request)

                if not available_charts:
                    available_charts = list(CHART_DEFINITIONS.keys())

                default_prefs = get_default_dashboard_preferences(available_charts)

                dashboard_prefs, created = DashboardPreferences.objects.get_or_create(
                    user=user,
                    defaults={
                        'layout': default_prefs['layout'],
                        'chart_definitions': default_prefs['chart_definitions'],
                        'filter_start_date': None,
                        'filter_end_date': None
                    }
                )

                if not created and force:   
                    dashboard_prefs.layout = default_prefs['layout']
                    dashboard_prefs.chart_definitions = default_prefs['chart_definitions']
                    dashboard_prefs.save()
                    
                    ChartSettings.objects.filter(dashboard_preferences=dashboard_prefs).delete()

                for chart_id in available_charts:
                    if chart_id in CHART_DEFINITIONS:
                        chart_setting, setting_created = ChartSettings.objects.get_or_create(
                            dashboard_preferences=dashboard_prefs,
                            chart_id=chart_id,
                            defaults={
                                'chart_type': CHART_DEFINITIONS[chart_id]['default_type'],
                                'size': CHART_DEFINITIONS[chart_id]['default_size'],
                                'enabled': True,
                                'start_date': None,
                                'end_date': None
                            }
                        )
                        
                        if not setting_created and force:
                            chart_setting.chart_type = CHART_DEFINITIONS[chart_id]['default_type']
                            chart_setting.size = CHART_DEFINITIONS[chart_id]['default_size']
                            chart_setting.enabled = True
                            chart_setting.save()

                initialized_count += 1

            except Exception as e:
                error_count += 1
                self.stdout.write(
                    self.style.ERROR(f'Error initializing preferences for user {user.email}: {str(e)}')
                )

        self.stdout.write(
            self.style.SUCCESS(
                f'\nCompleted!\n'
                f'  Initialized: {initialized_count}\n'
                f'  Migrated: {migrated_count}\n'
                f'  Skipped: {skipped_count}\n'
                f'  Errors: {error_count}\n'
                f'  Total: {total_users}'
            )
        )

