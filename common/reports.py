import shutil
from datetime import datetime
from typing import List

import pandas as pd
from dashboard.models import JGWCache

KEYS = ["locale", "origin", "destination", "organisation", "language"]
OPERATORS = {
    "Concordia": "Seasonal  Worker Scheme - Concordia",
    "AG Recruitment": "Seasonal Worker Scheme - AG Recruitment",
    "Generic": "Seasonal Worker Scheme - Generic",
    "Pro-Force": "Seasonal Worker Scheme - Pro-Force",
    "Fruitful Jobs": "Seasonal Worker Scheme - Fruitful Jobs",
}
unwanted_cols = ["", "deviceId", "undefined", "__v", "_id"]
demographic_cols = [
    "appId",
    "locale",
    "route",
    "language",
    "origin",
    "destination",
    "organisation",
    "factoryFarm",
    "createdAt",
    "updatedAt",
]
exclude_cols = [*unwanted_cols, *demographic_cols]


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


def get_inlinetotals_report(start, end, category):
    output_filename = f"{category}.xlsx"
    result = JGWCache.objects.filter(category=category, date_created=datetime.today().date()).first()
    df = pd.read_json(result.data, orient="records")
    df = df.loc[df["createdAt"].between(start, end, inclusive="both")]
    print(df.columns, df.head(30))
    try:
        write_to_xls_sheet(df, sheet_name="Inline-All", filename=output_filename)
    except FileNotFoundError:
        shutil.copy("./temp/preferences.xlsx", "./inline.xlsx")
        write_to_xls_sheet(df, sheet_name="Inline-All", filename=output_filename)
    for k, operator_name in OPERATORS.items():
        new_df = df.loc[df["organisation"] == operator_name]
        new_df = new_df.loc[~new_df["origin"].isin(["MY", "US", "KY", "UG", "TZ", "BD"])]
        write_to_xls_sheet(new_df, sheet_name=f"inline-{k}", filename=output_filename)
    return output_filename


def get_inlineqns_report(start, end, category):
    output_filename = "./inlineqns.xlsx"
    result = JGWCache.objects.filter(category=category, date_created=datetime.today().date()).first()
    df = pd.read_json(result.data, orient="records")
    df = df.loc[df["createdAt"].between(start, end, inclusive="both")]
    question_cols = [i for i in df.columns if i not in exclude_cols]
    print(df.columns, "\n\n", df.head(30), "\n", question_cols)
    try:
        write_to_xls_sheet(df, sheet_name="Inline-All", filename=output_filename, fields=question_cols)
    except FileNotFoundError:
        shutil.copy("./temp/preferences.xlsx", "./inlineqns.xlsx")
        write_to_xls_sheet(df, sheet_name="Inline-All", filename=output_filename, fields=question_cols)
    for k, operator_name in OPERATORS.items():
        new_df = df.loc[df["organisation"] == operator_name]
        new_df = new_df.loc[~new_df["origin"].isin(["MY", "US", "KY", "UG", "TZ", "BD"])]
        write_to_xls_sheet(new_df, sheet_name=f"inline-{k}", filename=output_filename, fields=question_cols)
    return output_filename
