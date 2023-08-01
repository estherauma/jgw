
from common.custom_libs.google_translate import pandas_translator_translate
from question.models import InlineQuestionResponseText, MessagingResponseOptionText, MessagingQuestionText


def translate_and_clean_messaging_question_question_fields():
    untranslated_question_texts = MessagingQuestionText.objects.filter(translated_text__isnull=True)
    for question_text in untranslated_question_texts:
        pandas_translated_text = pandas_translator_translate(question_text.text)
        question_text.translated_text = pandas_translated_text
        question_text.save()
        
        
def translate_and_clean_messaging_question_response_option_fields():
    untranslated_response_options = MessagingResponseOptionText.objects.filter(translated_option__isnull=True)
    for response_options in untranslated_response_options:
        translated_option = pandas_translator_translate(response_options.option)
        response_options.translated_option = translated_option
        response_options.save()
        
        
def translate_and_clean_messaging_question_fields():
    translate_and_clean_messaging_question_question_fields()
    translate_and_clean_messaging_question_response_option_fields()
    

def translate_and_clean_inline_question_response_fields():
    untranslated_response_texts = InlineQuestionResponseText.objects.filter(translated_text__isnull=True)
    for response_text in untranslated_response_texts:
        translated_text = pandas_translator_translate(response_text.text)
        response_text.translated_text = translated_text
        response_text.save()
        

def translate_and_clean_inline_question_fields():
    translate_and_clean_inline_question_response_fields()