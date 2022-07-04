from celery import shared_task
from common.retrieve_data import JGWApi as APIHelper
from common.retrieve_data import translate_to_eng

from dashboard.models import TranslatedQuestionText, TranslatedResponseText, TranslatedText

jgw_api = APIHelper()


@shared_task(name="get_jgw_data")
def fetch_API_data():
    for key in ["inline", "preferences", "messaging"]:
        jgw_api.get_data(key=key)


@shared_task(name="translate_to_eng")
def translate_API_data():
    def _doer(model, limit=50):
        untranslated_text = model.objects.filter(translation__is_null=True)
        if untranslated_text.exists():
            objs = []
            for obj in untranslated_text[:limit]:
                obj.translation = translate_to_eng(obj.original_text)
                objs.append(obj)
            model.objects.bulk_update(objs, ["translation"])

    for model in [TranslatedQuestionText, TranslatedResponseText, TranslatedText]:
        _doer(model)
