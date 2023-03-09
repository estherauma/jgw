from django.shortcuts import render

# Create your views here.
def home(request):
    routes = [
            "bangladesh -> malaysia",
            "indonesia -> malaysia",
            "burma -> malaysia",
            "Greece -> uk",
            "nepal -> malaysia",
            "bangladesh -> mauritius",
            "Romania -> uk",
            "kenya -> qatar",
            "madagascar -> mauritius",
            "india -> malaysia",
            "kenya -> uae",
            "Bangladesh -> uk",
            "Bulgaria -> uk",
            "uganda -> saudi",
            "kenya -> saudi",
            "Ukraine -> uk",
            "vietnam -> malaysia",
            "Other - The rest of the world -> uk",
            "India -> uk",
            "Italy -> uk",
            "pakistan -> malaysia"
        ]
    returning_data_list =  [68, 39, 36, 35, 27, 18, 19, 25, 10, 5, 4, 4, 3, 3, 3, 3, 2, 2, 1, 1, 1]
    unique_data_list = [100, 27, 55, 35, 27, 18, 12, 77, 10, 5, 4, 4, 3, 13, 3, 3, 2, 2, 13, 9, 1]

    return render(request, template_name="demo_dashboard/index.html", context={ 
            'routes':routes,
            'returning_data_list': returning_data_list,
            'unique_data_list': unique_data_list
    })


def demographics(request):
    return render(request, template_name="demo_dashboard/demographics.html")


def inline_question(request):
    return render(request, template_name="demo_dashboard/inline_question.html")