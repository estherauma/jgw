from django.db import transaction

from common.helpers.preference_helpers.organisation import get_organisation_data
from common.logger import KunfuPandaLogger
from events.models import ChaptersFeedbackStandard, ChaptersOpened


def update_chapters_feedback_org_info_from_organisation():
    """
    Update chapters feedback org_info with the matching OrganisationData instance.
    Only processes records where is_org_info_cleaned is False.

    Resolution order (via get_organisation_data), mirroring preference logic:
    1. If org_code is set on the record, look up OrganisationData by org_code.
    2. Otherwise, match by organisation name against org_info_list.
    3. Otherwise, use OrganisationData with code ONS.
    """
    kunfu_panda_logger = KunfuPandaLogger()
    update_count = 0

    with transaction.atomic():
        chapters_feedback_to_update = ChaptersFeedbackStandard.objects.filter(
            is_org_info_cleaned=False,
            organisation__isnull=False,
        ).select_related('organisation')

        kunfu_panda_logger.info(
            f"Found {chapters_feedback_to_update.count()} chapters feedback to process"
        )

        for chapters_feedback in chapters_feedback_to_update:
            org_code = getattr(chapters_feedback, 'org_code', None) or getattr(
                chapters_feedback, 'organisation_code', None
            )
            org_data = get_organisation_data(
                org_code=org_code,
                organisation=chapters_feedback.organisation,
            )

            chapters_feedback.org_info = org_data
            chapters_feedback.is_org_info_cleaned = True
            chapters_feedback.save()

            # Only count when we resolved to a specific org (not ONS fallback)
            if org_data.org_code != 'ONS':
                update_count += 1
                kunfu_panda_logger.info(
                    f"Updated org_info for chapters feedback {chapters_feedback.id} "
                    f"with org_code {org_data.org_code}"
                )

    kunfu_panda_logger.info(f"Updated org_info for {update_count} chapters feedback")
    return update_count

def update_chapters_opened_org_info_from_organisation():
    """
    Update chapters opened org_info with the matching OrganisationData instance.
    Only processes records where is_org_info_cleaned is False.

    Resolution order (via get_organisation_data), mirroring preference logic:
    1. If org_code is set on the record, look up OrganisationData by org_code.
    2. Otherwise, match by organisation name against org_info_list.
    3. Otherwise, use OrganisationData with code ONS.
    """
    kunfu_panda_logger = KunfuPandaLogger()
    update_count = 0

    with transaction.atomic():
        chapters_opened_to_update = ChaptersOpened.objects.filter(
            is_org_info_cleaned=False,
            organisation__isnull=False,
        ).select_related('organisation')

        kunfu_panda_logger.info(
            f"Found {chapters_opened_to_update.count()} chapters opened to process"
        )

        for chapters_opened in chapters_opened_to_update:
            org_code = getattr(chapters_opened, 'org_code', None) or getattr(
                chapters_opened, 'organisation_code', None
            )
            org_data = get_organisation_data(
                org_code=org_code,
                organisation=chapters_opened.organisation,
            )

            chapters_opened.org_info = org_data
            chapters_opened.is_org_info_cleaned = True
            chapters_opened.save()

            # Only count when we resolved to a specific org (not ONS fallback)
            if org_data.org_code != 'ONS':
                update_count += 1
                kunfu_panda_logger.info(
                    f"Updated org_info for chapters opened {chapters_opened.id} "
                    f"with org_code {org_data.org_code}"
                )

    kunfu_panda_logger.info(f"Updated org_info for {update_count} chapters opened")
    return update_count

