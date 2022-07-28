from datetime import datetime
from logging import getLogger

from celery import shared_task
from common.retrieve_data import JGWApi as APIHelper
from common.retrieve_data import translate_to_eng

from dashboard.models import TranslatedQuestionText, TranslatedResponseText, TranslatedText
from dashboard.views import get_report

jgw_api = APIHelper()
debug_logger = getLogger("djangoDebug")


@shared_task(name="get_jgw_data")
def fetch_API_data():
    for key in [
        "inline",
        "preferences",
        "messaging",
        "help_contacts",
        "visa",
        "joboffer",
        "contract",
        "beforeyougo",
    ]:
        jgw_api.get_data(key=key)


@shared_task(name="translate_to_eng")
def translate_API_data():
    def _doer(model, limit=50):
        untranslated_text = model.objects.filter(translation__isnull=True)
        if untranslated_text.exists():
            objs = []
            for obj in untranslated_text[:limit]:
                obj.translation = translate_to_eng(obj.original_text)
                objs.append(obj)
            model.objects.bulk_update(objs, ["translation"])

    for model in [TranslatedQuestionText, TranslatedResponseText, TranslatedText]:
        _doer(model)


@shared_task(name="generate_report")
def generate_report():
    today = datetime.today().strftime("%Y-%m-%d")
    week_number = int(datetime.today().strftime("%U"))
    if week_number % 2 == 0:
        return
    filename = get_report(start="2022-06-01", end=today, category="preferences")
    return filename
