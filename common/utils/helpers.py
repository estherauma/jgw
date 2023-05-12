import os
import pandas as pd

def save_as_excel(df, file_name='file'):
    excel_writer = pd.ExcelWriter(f'{file_name}.xlsx', engine='openpyxl')
    df.to_excel(excel_writer, index=False)
    excel_writer.close()


def remove_file(file_path):
    os.remove(file_path)