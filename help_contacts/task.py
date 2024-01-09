from common.custom_libs.google_translate import pandas_translator_translate
from common.logger import KunfuPandaLogger
from help_contacts.models import HelpContact

kunfu_panda_logger = KunfuPandaLogger(log_file="logs/help_contacts_tasks.log")


def translate_and_clean_help_contact_value_fields():
    untranslated_help_contact_values = HelpContact.objects.filter(translated_contact_value__isnull=True)
    for help_contact_value in untranslated_help_contact_values:
        pandas_translated_text = pandas_translator_translate(help_contact_value.contact_value)
        help_contact_value.translated_contact_value = pandas_translated_text
        help_contact_value.save()

    kunfu_panda_logger.info(f"{len(untranslated_help_contact_values)} help contact values translated")


def translate_and_clean_help_contact_fields():
    translate_and_clean_help_contact_value_fields()
