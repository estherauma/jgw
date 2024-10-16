import requests
from django.conf import settings
from preference.models import OriginalSectorOfWork


def process_and_store_original_work_sectors():
    try:
        data = fetch_work_sectors_data()

        if data:
            sectors_data = extract_work_sectors(data)
            save_work_sectors_to_db(sectors_data)
            print("Work sectors have been successfully saved to the database.")
        else:
            print("Failed to fetch or process the data.")
    except Exception as e:
        print(f"An error occurred in the process: {e}")


def fetch_work_sectors_data():
    try:
        url = f"{settings.JGW_API}appcontent/v2/work-sector-translations"
        headers = {"secret": settings.JGW_API_SECRET}

        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()
        return data
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data from API: {e}")
        return None
    except ValueError as e:
        print(f"Error parsing JSON response: {e}")
        return None
    except Exception as e:
        print(f"An unexpected error occurred while fetching work sector data: {e}")
        return None


def extract_work_sectors(data):
    try:
        if not data or data.get("status") != "OK":
            print("Invalid data received")
            return []

        work_sectors_list = []

        for content in data.get("data", []):
            language = content.get("language")
            for sector in content.get("workSectors", []):
                work_sectors_list.append(
                    {
                        "language": language,
                        "key": sector.get("key"),
                        "value": sector.get("value"),
                        "display_name": sector.get("displayName"),
                    }
                )

        return work_sectors_list
    except KeyError as e:
        print(f"Missing key in the response data: {e}")
        return []
    except Exception as e:
        print(f"An error occurred while extracting work sectors: {e}")
        return []


def save_work_sectors_to_db(sectors_data):
    try:
        if not sectors_data:
            print("No sectors data to save.")
            return

        for sector in sectors_data:
            try:
                OriginalSectorOfWork.objects.get_or_create(
                    language=sector["language"],
                    key=sector["key"],
                    defaults={"value": sector["value"], "display_name": sector["display_name"]},
                )
            except Exception as e:
                print(f"Error saving sector {sector['key']} to the database: {e}")
    except Exception as e:
        print(f"An error occurred while saving work sectors to the database: {e}")
