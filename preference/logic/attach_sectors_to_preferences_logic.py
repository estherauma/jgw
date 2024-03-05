import pandas as pd
from django.db.models.functions import Length

from common.helpers.model_helpers.preference import add_sector_of_work_to_db
from preference.models import Preference, SectorOfWork
from preference.repository.preference_mongo_repo import get_preference_from_mongo_db


def attach_sectors_to_preferences():
    """
    This retrieves sectors of work from mongodb database
    and attaches/assign them to preferences in the pandas postgreSQL database.
    """
    preferences_without_sectors_of_work = Preference.objects.filter(
        sectors_of_work__translated_name="not specified"
    )

    for preference_instance in preferences_without_sectors_of_work:

        the_id = preference_instance.data_source_id

        preference_from_mongo_db = get_preference_from_mongo_db(the_id)

        if preference_from_mongo_db:
            preference_instance.sectors_of_work.clear()

            sec_of_work_list = add_sector_of_work_to_db(preference_from_mongo_db["final_sectors"])
            for sec_of_work in sec_of_work_list:
                preference_instance.sectors_of_work.add(sec_of_work)


def strigified_sectors_of_work_to_list():
    preference_instances = Preference.objects.annotate(
        name_length=Length("sectors_of_work__translated_name")
    ).filter(name_length__lt=2)

    for preference_instance in preference_instances:
        preference_instance.sectors_of_work.clear()

        the_id = preference_instance.data_source_id
        preference_from_mongo_db = get_preference_from_mongo_db(the_id)

        sec_of_work_list = add_sector_of_work_to_db(preference_from_mongo_db["final_sectors"])
        for sec_of_work in sec_of_work_list:
            preference_instance.sectors_of_work.add(sec_of_work)

    sectors_of_work_to_delete = SectorOfWork.objects.annotate(name_length=Length("name")).filter(
        name_length__lt=2
    )
    sectors_of_work_to_delete.delete()


def clean_sectors_of_work():
    sectors_of_work = SectorOfWork.objects.all()
    for sector_of_work in sectors_of_work:

        if sector_of_work and not sector_of_work.translated_name:
            sector_of_work.translated_name = (
                sector_of_work.name.strip().lower().replace("&amp;", "and").replace("&", "and")
            )
        else:
            sector_of_work.translated_name = (
                sector_of_work.translated_name.strip().lower().replace("&amp;", "and").replace("&", "and")
            )

        sector_of_work.save()


def export_sectors_of_work_to_excel():
    sectors_of_work = SectorOfWork.objects.all()
    sectors_of_work_list = [
        {
            "name": sec.name,
            "translated_name": sec.translated_name,
        }
        for sec in sectors_of_work
    ]
    df = pd.DataFrame(sectors_of_work_list)
    df.to_excel("sectors_of_work.xlsx", index=False)
