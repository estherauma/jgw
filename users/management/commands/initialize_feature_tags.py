from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.db.models import Q
from waffle import get_waffle_flag_model


class Command(BaseCommand):
    help = "Create initial feature toggle tags for user groups using the waffle library"

    def handle(self, *args, **options):

        group_name = "testers"
        testers_group, _ = Group.objects.get_or_create(name=group_name)
        permissions = Permission.objects.filter(
            ~Q(content_type__app_label="users")
            & ~Q(content_type__app_label="admin")
            & ~Q(content_type__app_label="waffle")
            & ~Q(content_type__app_label="auth")
        )
        for permission in permissions:
            testers_group.permissions.add(permission)

        flags_list = [
            {"condition": "testers", "tag": "can_view_user_geolocation_map"},
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
            {"condition": "testers", "tag": "can_view_inline_questions_page"},
            {"condition": "testers", "tag": "can_view_new_monthly_users_chart"},
            {"condition": "testers", "tag": "can_view_get_users_by_country_state_chart"},
            {"condition": "testers", "tag": "can_view_get_users_by_sector_chart"},
            {"condition": "everyone", "tag": "can_download_worker_insights_excel_reports"},
            {"condition": "everyone", "tag": "can_download_messaging_questions_excel_reports"},
            {"condition": "everyone", "tag": "can_download_inline_questions_excel_reports"},
            {"condition": "everyone", "tag": "can_download_preferences_excel_reports"},
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
        WaffleFlag = get_waffle_flag_model()
        for flag in flags_list:
            created_flag, created = WaffleFlag.objects.get_or_create(name=flag["tag"], superusers=True)
            if flag["condition"] == "testers":
                created_flag.groups.add(testers_group)
            if flag["condition"] == "everyone":
                created_flag.everyone = True
                created_flag.save()
            self.stdout.write(
                self.style.SUCCESS(
                    f'Feature flag "{flag["tag"]}" for user group "{flag["condition"]}" initialized successfully.'
                )
            )
