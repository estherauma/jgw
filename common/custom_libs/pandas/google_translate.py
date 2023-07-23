from google.cloud import translate_v2 as translate


client = translate.Client()


def pandas_translator_translate(text: str, client=client, target_language="en") -> str:
    translate_text = client.translate(text, target_language=target_language)
    return translate_text["translatedText"]