def get_preferences_record(collection, query, projection):
    return collection.find(query, projection)


def process_sectors_data(record):
    sectors_of_work = record.get("sectors") or record.get("sectorsOfWork") or record.get("sectorOfWork") or []

    obj_id = record.get("_id")
    return {**record, "final_sectors_of_work": sectors_of_work, "string_id": str(obj_id) if obj_id else None}


def get_preference_from_mongo_db(mongodb_manager, preference_mong_ids):
    # dbs
    jgw_live_db = mongodb_manager.get_database("jgw_live")

    # collections
    preferences_col = jgw_live_db["preferences"]
    v2_preferences_col = jgw_live_db["v2_preferences"]
    v3_preferences_col = jgw_live_db["v3_preferences"]

    query = {"_id": {"$in": preference_mong_ids}}
    projection = {"sectors": 1, "sectorsOfWork": 1, "sectorOfWork": 1}

    preferences_record = get_preferences_record(preferences_col, query, projection)
    preferences_v2_record = get_preferences_record(v2_preferences_col, query, projection)
    preferences_v3_record = get_preferences_record(v3_preferences_col, query, projection)

    all_data = []
    if preferences_record:
        all_data.extend(preferences_record)

    if preferences_v2_record:
        all_data.extend(preferences_v2_record)

    if preferences_v3_record:
        all_data.extend(preferences_v3_record)

    final_sectors = [process_sectors_data(pref) for pref in all_data]

    return final_sectors
