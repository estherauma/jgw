from django.db import transaction
from question.models import InlineQuestionStandard, MessagingQuestionStandard, OrganisationData
from common.logger import KunfuPandaLogger
from common.const.value_const import org_info_list

def update_messaging_question_org_info_from_organisation():
    """
    Update messaging question org_info based on organisation name matching with org_info_list.
    Only processes preferences where is_missing_organisation_info_cleaned is False.
    """
    kunfu_panda_logger = KunfuPandaLogger()
    update_count = 0

    with transaction.atomic():
        messaging_question_to_update = MessagingQuestionStandard.objects.filter(
            is_org_info_cleaned=False
        ).select_related('organisation')

        kunfu_panda_logger.info(
            f"Found {messaging_question_to_update.count()} messaging question to process"
        )

        for messaging_question in messaging_question_to_update:
            ons_org_data = OrganisationData.objects.get(org_code='ONS')
            if messaging_question.organisation:
                org_name = messaging_question.organisation.name.lower().strip()
            else:
                messaging_question.org_info = ons_org_data
                messaging_question.is_org_info_cleaned = True
                messaging_question.save()
                continue
            
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
                    
                    messaging_question.org_info = org_data
                    messaging_question.is_org_info_cleaned = True
                    messaging_question.save()
                    
                    update_count += 1
                    kunfu_panda_logger.info(
                        f"Updated org_info for messaging question {messaging_question.id} "
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
                messaging_question.org_info = ons_org_data
                messaging_question.is_org_info_cleaned = True
                messaging_question.save()

    kunfu_panda_logger.info(f"Updated org_info for {update_count} messaging question")
    return update_count

def update_inline_question_org_info_from_organisation():
    """
    Update inline question org_info based on organisation name matching with org_info_list.
    Only processes preferences where is_missing_organisation_info_cleaned is False.
    """
    kunfu_panda_logger = KunfuPandaLogger()
    update_count = 0

    with transaction.atomic():
        inline_question_to_update = InlineQuestionStandard.objects.filter(
            is_org_info_cleaned=False,
            organisation__isnull=False
        ).select_related('organisation')

        kunfu_panda_logger.info(
            f"Found {inline_question_to_update.count()} inline question to process"
        )

        for inline_question in inline_question_to_update:
            org_name = inline_question.organisation.name.lower().strip()
            
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
                    
                    inline_question.org_info = org_data
                    inline_question.is_org_info_cleaned = True
                    inline_question.save()
                    
                    update_count += 1
                    kunfu_panda_logger.info(
                        f"Updated org_info for inline question {inline_question.id} "
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
                inline_question.is_org_info_cleaned = True
                inline_question.save()

    kunfu_panda_logger.info(f"Updated org_info for {update_count} inline question")
    return update_count
