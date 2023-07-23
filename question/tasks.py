
from common.custom_libs.pandas.google_translate import pandas_translator_translate
from question.models import MessagingQuestion, MessagingResponse


def translate_and_clean_question_fields():
    untranslated_questions = MessagingQuestion.objects.filter(translated_question__isnull=True)
    for question in untranslated_questions:
        translated_question = pandas_translator_translate(question.question)
        question.translated_question = translated_question
        question.save()
        
        
def translate_and_clean_response_fields():
    untranslated_responses = MessagingResponse.objects.filter(translated_option__isnull=True)
    for response in untranslated_responses:
        translated_option = pandas_translator_translate(response.option)
        response.translated_option = translated_option
        response.save()
        
        
def translate_and_clean_messaging_question_fields():
    translate_and_clean_question_fields()
    translate_and_clean_response_fields()