from django.db import transaction
from events.models import ChaptersFeedbackStandard, ChaptersOpened
from common.logger import KunfuPandaLogger
from preference.models import OrganisationData
from common.const.value_const import org_info_list

def update_chapters_feedback_org_info_from_organisation():
    """
    Update chapters feedback org_info based on organisation name matching with org_info_list.
    Only processes preferences where is_missing_organisation_info_cleaned is False.
    """
    kunfu_panda_logger = KunfuPandaLogger()
    update_count = 0

    with transaction.atomic():
        chapters_feedback_to_update = ChaptersFeedbackStandard.objects.filter(
            is_org_info_cleaned=False,
            organisation__isnull=False
        ).select_related('organisation')

        kunfu_panda_logger.info(
            f"Found {chapters_feedback_to_update.count()} chapters feedback to process"
        )

        for chapters_feedback in chapters_feedback_to_update:
            org_name = chapters_feedback.organisation.name.lower().strip()
            
            matching_org = next(
                (org for org in org_info_list 
                 if org["name"].lower().strip() == org_name),
                None
            )

            if matching_org:
                try:
                    org_data = OrganisationData.objects.get(
                        org_code=matching_org["org_code"]
                    )
                    chapters_feedback.org_info = org_data
                    chapters_feedback.is_org_info_cleaned = True
                    chapters_feedback.save()
                    
                    update_count += 1
                    kunfu_panda_logger.info(
                        f"Updated org_info for chapters feedback {chapters_feedback.id} "
                        f"with org_code {matching_org['org_code']}"
                    )
                except OrganisationData.DoesNotExist:
                    kunfu_panda_logger.warning(
                        f"No OrganisationData found for org_code: {matching_org['org_code']}"
                    )
            else:
                kunfu_panda_logger.warning(
                    f"No matching organization found for name: {org_name}"
                )
                chapters_feedback.is_org_info_cleaned = True
                chapters_feedback.save()

    kunfu_panda_logger.info(f"Updated org_info for {update_count} chapters feedback")
    return update_count

def update_chapters_opened_org_info_from_organisation():
    """
    Update chapters opened org_info based on organisation name matching with org_info_list.
    Only processes preferences where is_missing_organisation_info_cleaned is False.
    """
    kunfu_panda_logger = KunfuPandaLogger()
    update_count = 0

    with transaction.atomic():
        chapters_opened_to_update = ChaptersOpened.objects.filter(
            is_org_info_cleaned=False,
            organisation__isnull=False
        ).select_related('organisation')

        kunfu_panda_logger.info(
            f"Found {chapters_opened_to_update.count()} chapters opened to process"
        )

        for chapters_opened in chapters_opened_to_update:
            org_name = chapters_opened.organisation.name.lower().strip()

            matching_org = next(
                (org for org in org_info_list 
                 if org["name"].lower().strip() == org_name),
                None
            )

            if matching_org:
                try:
                    org_data = OrganisationData.objects.get(
                        org_code=matching_org["org_code"]
                    )
                    
                    chapters_opened.org_info = org_data
                    chapters_opened.is_org_info_cleaned = True
                    chapters_opened.save()
                    
                    update_count += 1
                    kunfu_panda_logger.info(
                        f"Updated org_info for chapters opened {chapters_opened.id} "
                        f"with org_code {matching_org['org_code']}"
                    )
                except OrganisationData.DoesNotExist:
                    kunfu_panda_logger.warning(
                        f"No OrganisationData found for org_code: {matching_org['org_code']}"
                    )
            else:
                kunfu_panda_logger.warning(
                    f"No matching organization found for name: {org_name}"
                )
                chapters_opened.is_org_info_cleaned = True
                chapters_opened.save()

    kunfu_panda_logger.info(f"Updated org_info for {update_count} chapters opened")
    return update_count

