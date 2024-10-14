from preference.models import OriginalSectorOfWork, SectorOfWork


def find_original_sector(sector):
    try:
        return OriginalSectorOfWork.objects.get(display_name__iexact=sector.name)
    except OriginalSectorOfWork.DoesNotExist:
        return None
    except OriginalSectorOfWork.MultipleObjectsReturned:

        return OriginalSectorOfWork.objects.filter(display_name__iexact=sector.name).first()


def update_original_sector_of_work_references():
    sectors_to_update = SectorOfWork.objects.filter(is_original_sector_of_work_in_english=False)
    updated_count = 0

    for sector in sectors_to_update:
        original_sector = find_original_sector(sector)
        if original_sector:
            sector.original_sector_of_work = original_sector
            sector.is_original_sector_of_work_in_english = True
            sector.save()

            updated_count += 1
        else:
            print(f"No matching OriginalSectorOfWork found for SectorOfWork: {sector.name}")

    return updated_count


def reset_is_original_sector_of_work_in_english_in_the_sector_of_work_table():

    SectorOfWork.objects.all().update(is_original_sector_of_work_in_english=False)
    SectorOfWork.objects.all().update(original_sector_of_work=None)
