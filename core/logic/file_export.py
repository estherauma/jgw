from django.http import HttpResponse
import openpyxl
from openpyxl.styles import Font, PatternFill
from openpyxl.utils import get_column_letter


def generate_and_export_excel(data):
    # Create a new Excel workbook
    wb = openpyxl.Workbook()

    for sheet_name, data_dict in data.items():
        ws = wb.create_sheet(title=sheet_name)

        for key, value in data_dict.items():
            ws.append(['', ''])
            title_cell = ws.cell(row=ws.max_row + 1, column=1, value=key.replace("_", " ").upper())
            title_cell.font = Font(bold=True)
            title_cell.fill = PatternFill(start_color='F2F2F2', end_color='F2F2F2', fill_type='solid')

            ws.append(['', 'LABELS', 'COUNTS'])
            labels = value['labels']
            counts = value['data']

            for label, count in zip(labels, counts):
                ws.append(['', label, count])

            # Make 'LABELS' and 'COUNTS' bold
            ws['B{}'.format(ws.max_row - 1)].font = Font(bold=True)
            ws['C{}'.format(ws.max_row - 1)].font = Font(bold=True)

        # Adjust column widths
        for column_cells in ws.columns:
            max_length = 0
            for cell in column_cells:
                try:
                    if len(str(cell.value)) > max_length:
                        max_length = len(cell.value)
                except:
                    pass
            adjusted_width = (max_length + 2) * 1.2
            ws.column_dimensions[column_cells[0].column_letter].width = adjusted_width

    # Remove the default empty sheet
    del wb[wb.sheetnames[0]]

    return generate_export_response(wb, 'output')


def generate_export_response(workbook, export_name):
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = f'attachment; filename={export_name}.xlsx'
    
    workbook.save(response)
    
    return response