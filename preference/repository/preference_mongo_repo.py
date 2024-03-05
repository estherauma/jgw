from bson.objectid import ObjectId

from common.services.mongodb_manager import MongoDBConnectionManager


def get_preferences_record(collection, query, projection):
    return collection.find_one(query, projection)


def process_sectors_data(record):
    return record.get("sectors") or record.get("sectorsOfWork") or []


def get_preference_from_mongo_db(preference_mong_id):
    mongodb_manager = MongoDBConnectionManager()

    # dbs
    jgw_live_db = mongodb_manager.get_database("jgw_live")

    # collections
    preferences_col = jgw_live_db["preferences"]
    v2_preferences_col = jgw_live_db["v2_preferences"]
    v3_preferences_col = jgw_live_db["v3_preferences"]

    # filter conditions
    query = {"_id": ObjectId(preference_mong_id)}
    projection = {"sectors": 1, "sectorsOfWork": 1}

    preferences_record = get_preferences_record(preferences_col, query, projection)
    preferences_v2_record = get_preferences_record(v2_preferences_col, query, projection)
    preferences_v3_record = get_preferences_record(v3_preferences_col, query, projection)

    data = {}
    if preferences_record:
        data["final_sectors"] = process_sectors_data(preferences_record)

    if preferences_v2_record:
        data["final_sectors"] = process_sectors_data(preferences_v2_record)

    if preferences_v3_record:
        data["final_sectors"] = process_sectors_data(preferences_v3_record)

    return data if data.get("final_sectors") else []
