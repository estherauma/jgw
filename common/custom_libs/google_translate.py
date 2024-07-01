from http.client import SERVICE_UNAVAILABLE, TOO_MANY_REQUESTS
import time
import requests
import six
from google.cloud import translate_v2 as translate


client = translate.Client()


def pandas_translator_translate(text: str, client=client, target_language="en", retries=3, delay=1) -> str:
    if text is None:
        return text

    if isinstance(text, six.binary_type):
        text = text.decode("utf-8")
        
    if isinstance(text, str):
        for attempt in range(retries):
            try:
                result = client.translate(text, target_language=target_language)
                return result["translatedText"]
            except (SERVICE_UNAVAILABLE, TOO_MANY_REQUESTS) as e:
                if attempt < retries - 1:
                    time.sleep(delay)
                    delay *= 2 
                else:
                    raise e
            except requests.exceptions.RequestException as e:
                if attempt < retries - 1:
                    time.sleep(delay)
                    delay *= 2 
                else:
                    raise e