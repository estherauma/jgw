import json
from datetime import datetime

from django.test import TestCase
from django.test.client import RequestFactory
from django.urls import reverse
from django.utils.http import urlencode

from common.reports import get_start_date
from dashboard.forms import ExportReportForm, FilterForm, InlineQnsForm
from dashboard.models import Factory, JGWCache, Scheme
from dashboard.views import redirect_to_filtered_data, summerberry_dummy_data
from users.models import User


class DashboardTests(TestCase):
    def setUp(self):
        super(DashboardTests, self).setUp()
        email, pword = "test@test.local", "12t32thome"
        for category in ["preferences", "inline"]:
            with open(f"./temp/{category}_test_data.json") as seed_file:
                JGWCache.objects.create(
                    category=category, is_cleaned=True, data=json.dumps(json.load(seed_file))
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
        self.assertIn("Location", response_dict)

    def test_filter_form_validation(self):
        form_data = {"destination": "Non-Existent Country"}
        url = reverse("dashboard:filter_data", args=("preferences",))
        response = self.client.post(url, data=form_data)
        self.assertEqual(response.status_code, 400)
        self.assertIn("form_errors", response.json())

    def test_get_origin_options(self):
        url = reverse("dashboard:process_origin_options", args=("preferences",))
        filters = {"destination": "Qatar"}
        expected_json = {
            "": "Select a Country",
            "Kenya": "Kenya",
            "Other - The Rest Of The World": "Other - The Rest Of The World",
            "Uganda": "Uganda",
        }
        # TODO: Fix this test
        # response = self.client.get(f"{url}?{urlencode(filters)}")
        # self.assertEqual(response.json(), expected_json)

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
        self.assertTemplateUsed(response, "dashboard/preferences.html")
        self.assertIsInstance(response.context["form"], FilterForm)

    def test_inline_qns_renders_correctly(self):
        url = reverse("dashboard:inline")
        response = self.client.get(url)
        self.assertTemplateUsed(response, "dashboard/inline.html")
        self.assertIsInstance(response.context["form"], InlineQnsForm)

    def test_messaging_qns_renders_correctly(self):
        url = reverse("dashboard:messaging")
        response = self.client.get(url)
        self.assertTemplateUsed(response, "dashboard/messaging.html")
        self.assertIsInstance(response.context["form"], FilterForm)

    def test_help_contacts_renders_correctly(self):
        url = reverse("dashboard:help_contacts")
        response = self.client.get(url)
        self.assertTemplateUsed(response, "dashboard/help_contacts.html")
        self.assertIsInstance(response.context["form"], FilterForm)

    def test_checklists_stats_renders_correctly(self):
        url = reverse("dashboard:checklists", args=("visa",))
        response = self.client.get(url)
        self.assertTemplateUsed(response, "dashboard/visa_checklists.html")
        self.assertIsInstance(response.context["form"], FilterForm)

    def test_batch_sws_report_export_renders_correctly(self):
        url = reverse("dashboard:export_report")
        response = self.client.get(url)
        self.assertTemplateUsed(response, "dashboard/batch_export.html")
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

    def test_summerberry_dummy_data_response_code(self):
        url = reverse("dashboard:summerberry-sample")
        response = self.client.get(url)
        assert response.status_code == 200

    def test_summerberry_dummy_data_response_type(self):
        url = reverse("dashboard:summerberry-sample")
        response = self.client.get(url)
        assert response['Content-Type'] == 'application/json'

    def test_summerberry_dummy_data_response_type(self):
        url = reverse("dashboard:summerberry-sample")
        response = self.client.get(url)
        assert response['Content-Type'] == 'application/json'

    def test_summerberry_dummy_data_item_fields(self):
        url = reverse("dashboard:summerberry-sample")
        response = self.client.get(url)
        data = json.loads(response.content)
        for item in data:
            assert 'name' in item
            assert 'number' in item
            assert 'start_date' in item
            assert 'reg_date' in item
            assert 'completed_registration' in item
            assert 'completed_induction' in item
            assert 'signed_contract' in item
            assert 'worker_directive_signed' in item
            assert 'hygiene_signed' in item
            assert 'medical_signed' in item
            assert isinstance(item['name'], str)
            assert isinstance(item['number'], int)
            assert isinstance(item['start_date'], str)
            assert isinstance(item['reg_date'], str)
            assert isinstance(item['completed_registration'], bool)
            assert isinstance(item['completed_induction'], str)
            assert isinstance(item['signed_contract'], bool)
            assert isinstance(item['worker_directive_signed'], str)
            assert isinstance(item['hygiene_signed'], bool)
            assert isinstance(item['medical_signed'], bool)


 
