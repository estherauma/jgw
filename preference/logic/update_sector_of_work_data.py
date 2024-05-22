from django.db import transaction

from common.services.api_client import JustGoodWorkAPIClient
from preference.models import Preference, SectorOfWork
def preferences_data_url(client):

    start_date = "2023-10-01"
    end_date = "2024-02-01"

    return client.get_data(f"/preferences?startDate={start_date}&endDate={end_date}")

@transaction.atomic
def fetch_preferences_data_from_api():
    jgw_api_client = JustGoodWorkAPIClient()
    preferences = preferences_data_url(jgw_api_client) or []

    for preference_data in preferences:
        data_source_id = preference_data.get("_id")
        organisationSector = preference_data.get("organisationSector")
        sectors = preference_data.get("sectors", [])

        if not sectors and not organisationSector:
            sectors_from_api = ["not specified"]
        else:
            sectors_from_api = sectors or [organisationSector]
        sector_primary_keys = []
        for sector_name in sectors_from_api:
            sector = SectorOfWork.objects.get(name=sector_name)
            sector_primary_keys.append(sector.pk)
        
        preference_object = Preference.objects.filter(data_source_id=data_source_id).first()
        if preference_object and sector_primary_keys:
            preference_object.sectors_of_work.set(sector_primary_keys)
            print(f"Sectors updated for data_source_id: {data_source_id}")