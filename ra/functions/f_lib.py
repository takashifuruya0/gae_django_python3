import requests
from django.conf import settings


def translate_en_to_ja(text):
    url = settings.SECRET['URL_TRANSLATE']
    params = {
        "source_language": "en",
        "target_language": "ja",
        "text": text,
    }
    r = requests.get(url, params=params)
    return r.json()['text_translated']


def translate_ja_to_en(text):
    url = settings.SECRET['URL_TRANSLATE']
    params = {
        "source_language": "ja",
        "target_language": "en",
        "text": text,
    }
    r = requests.get(url, params=params)
    return r.json()['text_translated']