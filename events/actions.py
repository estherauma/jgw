from django.http import HttpResponse
import openpyxl


def links_click(self, request, queryset):
    links_clicks = queryset.values("event_name", "link", "event_date")
    response = HttpResponse(content_type="application/ms-excel")
    response["Content-Disposition"] = "attachment; filename=links-click-data.xlsx"

    workbook = openpyxl.Workbook()
    worksheet = workbook.active
    worksheet.title = "Links Click Data"
    worksheet.append(["Event Name", "Link", "Event Date"])

    for obj in links_clicks:
        event_name = obj.get("event_name")
        event_date = obj.get("event_date")
        link = obj.get("link")

        worksheet.append([event_name, link, event_date])

    # Adjust column widths based on content length
    for column_cells in worksheet.columns:
        length = max(len(str(cell.value)) for cell in column_cells)
        worksheet.column_dimensions[column_cells[0].column_letter].width = length + 2  # Adding extra space

    workbook.save(response)
    return response
