
from common.custom_libs.pandas.google_translate import pandas_translator_translate
from question.models import InlineQuestionResponse, MessagingResponseOptionText, MessagingQuestionText


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
    untranslated_responses = InlineQuestionResponse.objects.filter(translated_response__isnull=True)
    for response in untranslated_responses:
        translated_option = pandas_translator_translate(response.response)
        response.translated_response = translated_option
        response.save()
        

def translate_and_clean_inline_question_fields():
    translate_and_clean_inline_question_response_fields()