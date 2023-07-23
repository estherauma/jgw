import six
from google.cloud import translate_v2 as translate


client = translate.Client()


def pandas_translator_translate(text: str, client=client, target_language="en") -> str:
    if text is None:
        translated_text = text
        
    if isinstance(text, six.binary_type):
        translated_text = text.decode("utf-8")
        
    if isinstance(text, str):
        result = client.translate(text, target_language=target_language)
        translated_text = result["translatedText"]
        
    return translated_text