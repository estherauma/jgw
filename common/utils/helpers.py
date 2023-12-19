import os
import numpy as np
import pandas as pd


def save_as_excel(df, file_name="file"):
    excel_writer = pd.ExcelWriter(f"{file_name}.xlsx", engine="openpyxl")
    df.to_excel(excel_writer, index=False)
    excel_writer.close()


def remove_file(file_path):
    os.remove(file_path)


def dictionary_from_two_lists(labels, values):
    """Creates a dictionary from two lists

    Args:
        labels (_list_): to be used as keys
        values (_list_): to be used as values

    Returns:
        _type_: returns a dictionary
    """
    new_dict = {}

    for label, value in zip(labels, values):
        value = int(value) if type(value) == np.int64 else value
        new_dict[label] = value

    return new_dict


def can_use_cached_data():
    return os.environ.get("DEBUG") and os.environ.get("DATA_FROM_FILE")
