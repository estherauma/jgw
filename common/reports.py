import shutil
from datetime import datetime, timedelta
from typing import List

import pandas as pd
from dashboard.models import JGWCache

from .retrieve_data import exclude_cols

KEYS = ["locale", "origin", "destination", "organisation", "language"]
OPERATORS = {
    "Concordia": "Seasonal  Worker Scheme - Concordia",
    "AG Recruitment": "Seasonal Worker Scheme - AG Recruitment",
    "Generic": "Seasonal Worker Scheme - Generic",
    "Pro-Force": "Seasonal Worker Scheme - Pro-Force",
    "Fruitful Jobs": "Seasonal Worker Scheme - Fruitful Jobs",
}


def get_start_date(days, format="%Y-%m-%d"):
    target_date = datetime.today() - timedelta(days=days)
    return target_date.strftime(format)


def write_to_xls_sheet(df: pd.DataFrame, sheet_name: str, filename: str, fields: List = KEYS):
    with pd.ExcelWriter(filename, mode="a", if_sheet_exists="overlay") as writer:
        startrow = 0
        for key in fields:
            count = count_unique_series(df, key)
            count.to_excel(writer, sheet_name=sheet_name, startcol=0, startrow=startrow)
            startrow += count.size + 1


def count_unique_series(df: pd.DataFrame, key: str) -> pd.Series:
    if key in df.columns:
        return df[key].value_counts()
    return


def get_SWS_report(start, end, category):
    filenames = {
        "preferences": "demographics",
        "chapters": "chapters",
        "inlineQNs_participation": "inlineQNs_participation",
        "inlineQNs_responses": "inlineQNs_responses",
    }
    if category == "inlineQNs_responses":
        return get_inlineQNs_responses_report(start, end)
    output_filename = f"{filenames[category]}_{start}_{end}.xlsx"
    result = JGWCache.objects.filter(category=category, date_created=datetime.today().date()).first()
    df = pd.read_json(result.data, orient="records")
    df = df.loc[df["createdAt"].between(start, end, inclusive="both")]

    try:
        write_to_xls_sheet(df, sheet_name=f"{category[:8]}-All", filename=output_filename)
    except FileNotFoundError:
        shutil.copy("./temp/preferences.xlsx", output_filename)
        write_to_xls_sheet(df, sheet_name=f"{category[:8]}-All", filename=output_filename)
    for k, operator_name in OPERATORS.items():
        new_df = df.loc[df["organisation"] == operator_name]
        new_df = new_df.loc[~new_df["origin"].isin(["MY", "US", "KY", "UG", "TZ", "BD"])]
        write_to_xls_sheet(new_df, sheet_name=f"{category[:8]}-{k}", filename=output_filename)
    return output_filename


def get_inlineQNs_responses_report(start, end):
    output_filename = f"./inlineQNs_responses_{start}_{end}.xlsx"
    result = JGWCache.objects.filter(category="inline", date_created=datetime.today().date()).first()
    df = pd.read_json(result.data, orient="records")
    df = df.loc[df["createdAt"].between(start, end, inclusive="both")]
    question_cols = [i for i in df.columns if i not in exclude_cols]
    try:
        write_to_xls_sheet(df, sheet_name="Inline-All", filename=output_filename, fields=question_cols)
    except FileNotFoundError:
        shutil.copy("./temp/preferences.xlsx", output_filename)
        write_to_xls_sheet(df, sheet_name="Inline-All", filename=output_filename, fields=question_cols)
    for k, operator_name in OPERATORS.items():
        new_df = df.loc[df["organisation"] == operator_name]
        new_df = new_df.loc[~new_df["origin"].isin(["MY", "US", "KY", "UG", "TZ", "BD"])]
        write_to_xls_sheet(new_df, sheet_name=f"inline-{k}", filename=output_filename, fields=question_cols)
    return output_filename


def get_chapters_report(start, end):
    from .app_events import AppEvents

    a = AppEvents()
    output_filename = f"chapters_{start}_{end}.xlsx"
    data = a.get_data(start, end)
    chapters_df = data["chapters"]
    chapters_df.to_excel(output_filename)
    return output_filename
