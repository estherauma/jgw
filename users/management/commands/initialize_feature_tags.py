from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.db.models import Q
from waffle import get_waffle_flag_model
from users.utils import ALL_GROUPS
from users.models import User
from user_management.flags import UM_FLAG_DEFS


class Command(BaseCommand):
    help = "Create initial feature toggle tags for user groups using the waffle library"

    def handle(self, *args, **options):
        for group_name in ALL_GROUPS:
            Group.objects.get_or_create(name=group_name)
        # Todo:  remove this in next pr
        # Ensure all users with app access are in the worker group
        worker_group, _ = Group.objects.get_or_create(name="worker")
        app_users = User.objects.filter(access_type="app").exclude(groups=worker_group)
        if app_users.exists():
            for user in app_users:
                user.groups.add(worker_group)

        testers_group, _ = Group.objects.get_or_create(name='testers')
        permissions = Permission.objects.filter(
            ~Q(content_type__app_label="users")
            & ~Q(content_type__app_label="admin")
            & ~Q(content_type__app_label="waffle")
            & ~Q(content_type__app_label="auth")
        )
        for permission in permissions:
            testers_group.permissions.add(permission)

        flags_list = [
            {"condition": "testers", "tag": "can_view_user_geolocation_map_chart_on_user_engagement"},
            {"condition": "testers", "tag": "can_view_user_geolocation_map"},
            {"condition": "testers", "tag": "can_view_user_geolocation_map_chart_on_messaging_question_page"},
            {"condition": "testers", "tag": "can_view_messaging_question_by_sectors_on_messaging_page"},
            {"condition": "testers", "tag": "can_view_link_clicks_chart"},
            {"condition": "testers", "tag": "can_view_users_by_immigration_status_chart"},
            {"condition": "testers", "tag": "can_view_user_route_map_chart"},
            {"condition": "testers", "tag": "can_view_other_resources"},
            {"condition": "testers", "tag": "can_add_other_resources"},
            {"condition": "testers", "tag": "can_edit_other_resources"},
            {"condition": "testers", "tag": "can_delete_other_resources"},
            {"condition": "testers", "tag": "can_view_what_matters_to_workers_page"},
            {"condition": "testers", "tag": "can_view_messaging_question_report_export_button"},
            {"condition": "testers", "tag": "can_view_messaging_questions_page"},
            {"condition": "testers", "tag": "can_view_age_chart_on_messaging_question_page"},
            {"condition": "testers", "tag": "can_view_gender_chart_on_messaging_question_page"},
            {"condition": "testers", "tag": "can_view_organisation_chart_on_messaging_question_page"},
            {"condition": "testers", "tag": "can_view_inline_questions_page"},
            {"condition": "testers", "tag": "can_view_user_insights_page"},
            {"condition": "testers", "tag": "can_view_new_monthly_users_chart"},
            {"condition": "testers", "tag": "can_view_get_users_by_country_state_chart"},
            {"condition": "testers", "tag": "can_view_get_users_by_sector_chart"},
            {"condition": "testers", "tag": "can_view_language_select_button"},
            {"condition": "everyone", "tag": "can_download_worker_insights_excel_reports"},
            {"condition": "everyone", "tag": "can_download_telephone_clicks_data_report"},
            {"condition": "everyone", "tag": "can_download_link_clicks_data_report"},
            {"condition": "everyone", "tag": "can_download_report_issue_data_report"},
            {"condition": "everyone", "tag": "can_download_worker_insights_statistics_report"},
            {"condition": "everyone", "tag": "can_download_messaging_questions_excel_reports"},
            {"condition": "everyone", "tag": "can_download_messaging_questions_data_report"},
            {"condition": "everyone", "tag": "can_download_messaging_questions_pushed_data_report"},
            {"condition": "everyone", "tag": "can_download_messaging_questions_statistics_report"},
            {"condition": "everyone", "tag": "can_download_inline_questions_excel_reports"},
            {"condition": "everyone", "tag": "can_download_inline_questions_data_report"},
            {"condition": "everyone", "tag": "can_download_inline_questions_statistics_report"},
            {"condition": "everyone", "tag": "can_download_lead_questions_with_followups_report"},
            {"condition": "everyone", "tag": "can_download_preferences_excel_reports"},
            {"condition": "everyone", "tag": "can_download_preferences_data_report"},
            {"condition": "everyone", "tag": "can_download_help_contacts_data_report"},
            {"condition": "everyone", "tag": "can_download_preferences_statistics_report"},
            {"condition": "everyone", "tag": "can_download_pay_calculator_statistics_report"},
            {"condition": "everyone", "tag": "can_view_monthly_active_users_chart"},
            {"condition": "everyone", "tag": "can_view_messaging_question_responses_on_messaging_page"},
            {"condition": "everyone", "tag": "can_view_new_users_total_count"},
            {"condition": "everyone", "tag": "can_view_users_by_origin_country_chart"},
            {"condition": "everyone", "tag": "can_view_users_by_gender_chart"},
            {"condition": "everyone", "tag": "can_view_users_by_destination_country_chart"},
            {"condition": "everyone", "tag": "can_view_selected_users_language_chart"},
            {"condition": "everyone", "tag": "can_view_work_code_usage_chart"},
            {"condition": "everyone", "tag": "can_view_users_by_age_chart"},
            {"condition": "everyone", "tag": "can_view_users_by_month_chart"},
            {"condition": "everyone", "tag": "can_view_users_by_state_chart"},
            {"condition": "everyone", "tag": "can_view_users_by_sectors_chart"},
            {
                "condition": "everyone",
                "tag": "can_view_total_inline_questions_response_count_on_inline_question_page",
            },
            {"condition": "everyone", "tag": "can_view_organisation_chart_on_inline_question_page"},
            {"condition": "everyone", "tag": "can_view_selected_user_language_chart_on_inline_question_page"},
            {
                "condition": "everyone",
                "tag": "can_view_responses_per_origin_country_chart_on_inline_question_page",
            },
            {
                "condition": "everyone",
                "tag": "can_view_responses_per_destination_country_chart_on_inline_question_page",
            },
            {
                "condition": "everyone",
                "tag": "can_view_inline_question_responses_chart_on_inline_question_page",
            },
            {"condition": "everyone", "tag": "can_view_total_messaging_questions_count_on_messaging_page"},
            {"condition": "everyone", "tag": "can_view_messaging_question_per_origin_on_messaging_page"},
            {"condition": "everyone", "tag": "can_view_messaging_question_per_destination_on_messaging_page"},
            {"condition": "everyone", "tag": "can_view_organisation_chart_on_messaging_question_page"},
        ]
        um_flags = {flag["name"] for flag in UM_FLAG_DEFS}
        flags_list = [entry for entry in flags_list if entry["tag"] not in um_flags]
        for flag in UM_FLAG_DEFS:
            flags_list.append(
                {
                    "condition": flag.get("condition", "org_admin"),
                    "tag": flag["name"],
                }
            )
        WaffleFlag = get_waffle_flag_model()
        ROLE_INHERITANCE = {
            "org_admin": ["org_admin", "org_group_admin", "58_admin"],  # 58_admin and org_group_admin have all org_admin permissions
            "org_group_admin": ["org_group_admin", "58_admin"],  # 58_admin has all org_group_admin permissions
            "58_admin": ["58_admin"],  # 58_admin permissions only
            "user_management": ["user_management", "58_admin"],
        }
        EXCLUDED_58_ADMIN_FLAGS = {}  # to add any flags that should not be assigned to 58_admin group
  
        for flag in flags_list:
            created_flag, created = WaffleFlag.objects.get_or_create(name=flag["tag"], superusers=True)
            if flag["condition"] == "testers":
                created_flag.groups.add(testers_group)
            if flag["condition"] in ROLE_INHERITANCE:
                for group_name in ROLE_INHERITANCE[flag["condition"]]:
                    group, _ = Group.objects.get_or_create(name=group_name)
                    created_flag.groups.add(group)
            if flag["tag"] not in EXCLUDED_58_ADMIN_FLAGS:
                admin_58_group, _ = Group.objects.get_or_create(name="58_admin")
                created_flag.groups.add(admin_58_group)
            if flag["condition"] == "everyone":
                created_flag.everyone = True
                created_flag.save()
            self.stdout.write(
                self.style.SUCCESS(
                    f'Feature flag "{flag["tag"]}" for user group "{flag["condition"]}" initialized successfully.'
                )
            )
        
