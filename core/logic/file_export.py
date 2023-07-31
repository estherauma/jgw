from django.http import HttpResponse
from openpyxl import Workbook
from openpyxl.utils import get_column_letter


def create_workbook(work_sheets_data):
    workbook = Workbook()
    
    for work_sheet_data in work_sheets_data:
        name = work_sheet_data['name']
        headers = work_sheet_data['headers']
        contents = work_sheet_data['contents']

        sheet = workbook.create_sheet(title=name)

        sheet.append(headers)

        for content_row in contents:
            sheet.append(content_row)
            
        for col in sheet.columns:
            max_length = 0
            for cell in col:
                try:
                    if len(str(cell.value)) > max_length:
                        max_length = len(cell.value)
                except:
                    pass
            adjusted_width = (max_length + 2) * 1.2
            sheet.column_dimensions[get_column_letter(col[0].column)].width = adjusted_width
    
    workbook.active = 1
    
    return workbook


def generate_export_response(workbook, export_name):
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = f'attachment; filename={export_name}.xlsx'
    
    workbook.save(response)
    
    return response