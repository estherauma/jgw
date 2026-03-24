from django.db import transaction
from common.logger import KunfuPandaLogger
from events.models import BigqueryHomepageEventData
from preference.models import Preference, OrganisationData, PreferenceHistory
from common.const.value_const import org_info_list


def update_preferences_org_info_from_organisation():
    """
    Update preference org_info with the matching OrganisationData instance.
    Only processes preferences where is_missing_organisation_info_cleaned is False.

    Resolution order:
    1. If preference.org_code is set, look up OrganisationData by org_code and set org_info.
    2. Otherwise, match by organisation name against org_info_list and set org_info from that.
    """
    kunfu_panda_logger = KunfuPandaLogger()
    update_count = 0

    with transaction.atomic():
        preferences_to_update = Preference.objects.filter(
            is_missing_organisation_info_cleaned=False,
        ).select_related('organisation')

        kunfu_panda_logger.info(
            f"Found {preferences_to_update.count()} preferences to process"
        )

        for preference in preferences_to_update:
            org_data = None
            source = None

            # 1. Prefer org_code if set: look up OrganisationData by code
            if preference.org_code and preference.org_code.strip():
                try:
                    org_data = OrganisationData.objects.get(
                        org_code=preference.org_code.strip()
                    )
                    source = "org_code"
                except OrganisationData.DoesNotExist:
                    kunfu_panda_logger.warning(
                        f"No OrganisationData found for org_code: {preference.org_code!r}"
                    )

            # 2. Fallback: match by organisation name via org_info_list
            if org_data is None and preference.organisation:
                org_name = preference.organisation.name.lower().strip()
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
                        source = "organisation_name"
                    except OrganisationData.DoesNotExist:
                        kunfu_panda_logger.warning(
                            f"No OrganisationData found for org_code: {matching_org['org_code']}"
                        )
                else:
                    org_data = OrganisationData.objects.get(org_code='ONS')
                    kunfu_panda_logger.warning(
                        f"No matching organization found for name: {org_name}"
                    )

            preference.org_info = org_data
            preference.is_missing_organisation_info_cleaned = True
            preference.save()

            if org_data and source:
                update_count += 1
                kunfu_panda_logger.info(
                    f"Updated org_info for preference {preference.data_source_id} "
                    f"with org_code {org_data.org_code} (source: {source})"
                )

    kunfu_panda_logger.info(f"Updated org_info for {update_count} preferences")
    return update_count


def update_bigquery_homepage_event_org_info_from_organisation():
    """
    Update bigquery homepage event org_info with the matching OrganisationData instance.
    Only processes records where is_org_info_cleaned is False.

    Resolution order:
    1. If organisation_code is set, look up OrganisationData by org_code and set org_info.
    2. Otherwise, match by organisation name against org_info_list and set org_info from that.
    3. Otherwise, use OrganisationData with code ONS.
    """
    kunfu_panda_logger = KunfuPandaLogger()
    update_count = 0

    with transaction.atomic():
        bigquery_homepage_event_to_update = BigqueryHomepageEventData.objects.filter(
            is_org_info_cleaned=False,
            organisation__isnull=False
        ).select_related('organisation')

        kunfu_panda_logger.info(
            f"Found {bigquery_homepage_event_to_update.count()} bigquery homepage event to process"
        )

        for bigquery_homepage_event in bigquery_homepage_event_to_update:
            org_data = None
            source = None

            # 1. Prefer organisation_code if set: look up OrganisationData by code
            if bigquery_homepage_event.organisation_code and bigquery_homepage_event.organisation_code.strip():
                try:
                    org_data = OrganisationData.objects.get(
                        org_code=bigquery_homepage_event.organisation_code.strip()
                    )
                    source = "organisation_code"
                except OrganisationData.DoesNotExist:
                    kunfu_panda_logger.warning(
                        f"No OrganisationData found for org_code: {bigquery_homepage_event.organisation_code!r}"
                    )

            # 2. Fallback: match by organisation name via org_info_list
            if org_data is None and bigquery_homepage_event.organisation:
                org_name = bigquery_homepage_event.organisation.name.lower().strip()
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
                        source = "organisation_name"
                    except OrganisationData.DoesNotExist:
                        kunfu_panda_logger.warning(
                            f"No OrganisationData found for org_code: {matching_org['org_code']}"
                        )
                else:
                    org_data = OrganisationData.objects.get(org_code='ONS')
                    kunfu_panda_logger.warning(
                        f"No matching organization found for name: {org_name}"
                    )

            bigquery_homepage_event.org_info = org_data
            bigquery_homepage_event.is_org_info_cleaned = True
            bigquery_homepage_event.save()

            if org_data and source:
                update_count += 1
                kunfu_panda_logger.info(
                    f"Updated org_info for bigquery homepage event {bigquery_homepage_event.id} "
                    f"with org_code {org_data.org_code} (source: {source})"
                )

    kunfu_panda_logger.info(f"Updated org_info for {update_count} bigquery homepage events")
    return update_count
def update_preferences_journal_org_info_from_organisation():
    """
    Update preference journal org_info based on organisation name matching with org_info_list.
    Only processes preferences where is_missing_organisation_info_cleaned is False.
    """
    kunfu_panda_logger = KunfuPandaLogger()
    update_count = 0

    with transaction.atomic():
        preferences_to_update = PreferenceHistory.objects.filter(
            is_missing_organisation_info_cleaned=False,
            organisation__isnull=False
        ).select_related('organisation')

        kunfu_panda_logger.info(
            f"Found {preferences_to_update.count()} preferences journal to process"
        )

        for preference in preferences_to_update:
            org_name = preference.organisation.name.lower().strip()
            
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
                    
                    preference.org_info = org_data
                    preference.is_missing_organisation_info_cleaned = True
                    preference.save()
                    
                    update_count += 1
                    kunfu_panda_logger.info(
                        f"Updated org_info for preference journal {preference.data_source_id} "
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
                preference.is_missing_organisation_info_cleaned = True
                preference.save()

    kunfu_panda_logger.info(f"Updated org_info for {update_count} preferences journal")
    return update_count
