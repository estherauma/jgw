import time
import requests
import six
from google.cloud import translate_v2 as translate


client = translate.Client()

# HTTP status codes for retry (rate limit and service unavailable)
RETRY_STATUS_CODES = (429, 503)


def _is_retryable_http_error(exc):
    """True if exc is an HTTP error with 429 or 503."""
    if not isinstance(exc, requests.exceptions.HTTPError):
        return False
    return getattr(getattr(exc, "response", None), "status_code", None) in RETRY_STATUS_CODES


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
            except requests.exceptions.HTTPError as e:
                if _is_retryable_http_error(e) and attempt < retries - 1:
                    time.sleep(delay)
                    delay *= 2
                else:
                    raise
            except requests.exceptions.RequestException as e:
                if attempt < retries - 1:
                    time.sleep(delay)
                    delay *= 2
                else:
                    raise