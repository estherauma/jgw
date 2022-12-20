import json
from datetime import datetime, timedelta
from pprint import pprint

from django.contrib.messages.storage.cookie import CookieStorage
from django.test import TestCase
from django.test.client import RequestFactory
from django.urls import reverse
from django.utils.http import urlencode

from common.preferences import Preferences
from common.reports import get_start_date
from dashboard.forms import ExportReportForm, FilterForm, InlineQnsForm
from dashboard.models import Factory, JGWCache, Scheme
from dashboard.views import redirect_to_filtered_data, render_data
from users.models import User


class DashboardTests(TestCase):
    def setUp(self):
        super(DashboardTests, self).setUp()
        email, pword = "test@test.local", "12t32thome"
        with open("./temp/preferences_test_data.json") as seed_file:
            JGWCache.objects.create(
                category="preferences", is_cleaned=True, data=json.dumps(json.load(seed_file))
            )
        _ = (Scheme.objects.create(name=f"testScheme_{i}") for i in (1, 2))
        _ = (Factory.objects.create(name=f"testFactory_{i}", scheme_id=i) for i in (1, 2))
        self.test_user = User.objects.create_user(email=email, password=pword, is_active=True)
        self.client.login(email=email, password=pword)
        self.factory = RequestFactory()
        self.today = datetime.today().strftime("%Y-%m-%d")

    def test_redirect_to_filtered_data_OK(self):
        form_data = {"destination": "Britain (Uk)"}
        url = reverse("dashboard:preferences")
        template_name = "preferences.html"
        request = self.factory.post(url, form_data)
        response = redirect_to_filtered_data(request=request, url=url, template_name=template_name)
        self.assertEqual(response.status_code, 302)
        response_dict = dict(response.items())
        self.assertEqual(response_dict["Location"], f"{url}?{urlencode(form_data)}")

    def test_filter_form_validation(self):
        form_data = {"destination": "Non-Existent Country"}
        url = reverse("dashboard:preferences")
        template_name = "preferences.html"
        request = self.factory.post(url, form_data)
        response = redirect_to_filtered_data(request=request, url=url, template_name=template_name)
        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response, "Select a valid choice. Non-Existent Country is not one of the available choices."
        )

    def test_render_data_OK(self):
        def prepare_request(request):
            request.user = self.test_user
            request._messages = CookieStorage(request)
            return request

        def prepare_url(url, filters):
            url = f"{url}?" if filters else url
            for k, v in filters.items():
                url += f"{k}={v}&"
            return url

        _empty = {}
        _not_found = {"destination": "Non-Existent Country"}
        _time_range = {"time_range": get_start_date(days=30)}
        _start_date = {
            "start_date": get_start_date(days=30),
            "end_date": self.today,
        }
        url = reverse("dashboard:preferences")
        template_name = "preferences.html"

        requests = [
            self.factory.get(f"{prepare_url(url,query)}") for query in (_empty, _time_range, _start_date)
        ]
        responses = [
            render_data(request=prepare_request(request), template_name=template_name, helper=Preferences())
            for request in requests
        ]
        for response in responses:
            self.assertContains(response, 'new Chart(document.getElementById("_" + "age")')
            self.assertEqual(response.status_code, 200)

        request = self.factory.get(f"{prepare_url(url,_not_found)}")
        response = render_data(
            request=prepare_request(request), template_name=template_name, helper=Preferences()
        )
        self.assertContains(response, "No data matches this search!")

    def test_get_origin_options(self):
        url = reverse("dashboard:process_origin_options", args=("preferences",))
        filters = {"destination": "Qatar"}
        expected_json = {
            "": "Select a Country",
            "Britain (Uk)": "Britain (Uk)",
            "India": "India",
            "Indonesia": "Indonesia",
            "Kenya": "Kenya",
            "Kyrgyzstan": "Kyrgyzstan",
            "Nepal": "Nepal",
            "Other - The Rest Of The World": "Other - The Rest Of The World",
            "Uganda": "Uganda",
            "Uzbekistan": "Uzbekistan",
        }
        response = self.client.get(f"{url}?{urlencode(filters)}")
        self.assertEqual(response.json(), expected_json)

    def test_get_factory_options(self):
        url = reverse("dashboard:process_factory_options", args=("preferences",))
        filters = {"scheme_name": "testScheme_1"}
        expected_json = {"": "Select a Factory or Farm"}
        response = self.client.get(f"{url}?{urlencode(filters)}")
        self.assertEqual(response.json(), expected_json)
        self.assertEqual(response.status_code, 200)

    def test_export_to_excel_file(self):
        url = reverse("dashboard:export_to_excel", args=("preferences",))
        filters = {"destination": "Britain (Uk)", "time_range": f"{get_start_date(days=30)},{self.today}"}
        response = self.client.get(f"{url}?{urlencode(filters)}")
        expected_filename = f"demographics_"
        self.assertIn(expected_filename, response.headers["Content-Disposition"])
        self.assertEqual(
            response.headers["Content-Type"],
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )

    def test_export_to_excel_file_unknown_category(self):
        url = reverse("dashboard:export_to_excel", args=("non_existent_category",))
        filters = {"destination": "Britain (Uk)", "time_range": f"{get_start_date(days=30)},{self.today}"}
        response = self.client.get(f"{url}?{urlencode(filters)}")
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("dashboard:preferences"))
    
    def test_demographics_renders_correctly(self):
        url = reverse("dashboard:preferences")
        response = self.client.get(url)
        self.assertTemplateUsed(response, "preferences.html")
        self.assertIsInstance(response.context["form"], FilterForm)
    
    def test_inline_qns_renders_correctly(self):
        url = reverse("dashboard:inline")
        response = self.client.get(url)
        self.assertTemplateUsed(response, "inline.html")
        self.assertIsInstance(response.context["form"], InlineQnsForm)
    
    def test_messaging_qns_renders_correctly(self):
        url = reverse("dashboard:messaging")
        response = self.client.get(url)
        self.assertTemplateUsed(response, "messaging.html")
        self.assertIsInstance(response.context["form"], FilterForm)
    
    def test_help_contacts_renders_correctly(self):
        url = reverse("dashboard:help_contacts")
        response = self.client.get(url)
        self.assertTemplateUsed(response, "help_contacts.html")
        self.assertIsInstance(response.context["form"], FilterForm)

    def test_checklists_stats_renders_correctly(self):
        url = reverse("dashboard:checklists", args=('visa',))
        response = self.client.get(url)
        self.assertTemplateUsed(response, "visa_checklists.html")
        self.assertIsInstance(response.context["form"], FilterForm) 

    def test_batch_sws_report_export_renders_correctly(self):
        url = reverse("dashboard:export_report")
        response = self.client.get(url)
        self.assertTemplateUsed(response, "batch_export.html")
        self.assertIsInstance(response.context["form"], ExportReportForm)

    def test_batch_sws_report_export(self):
        url = reverse("dashboard:export_report")
        form_data = {
            "category": "preferences",
            "start_date": f"{get_start_date(days=30)}",
            "end_date": self.today,
        }
        response = self.client.post(url, form_data)
        expected_filename = f"demographics_"
        self.assertIn(expected_filename, response.headers["Content-Disposition"])
        self.assertEqual(
            response.headers["Content-Type"],
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )

    def test_batch_sws_report_export_form_validation(self):
        url = reverse("dashboard:export_report")
        form_data = {
            "category": "preferences",
            "start_date": f"{get_start_date(days=30)}",
            "end_date": datetime.today(),
        }
        response = self.client.post(url, form_data)
        form_errors = dict(response.context["form"].errors)
        self.assertEqual(form_errors, {"end_date": ["Enter a valid date."]})
