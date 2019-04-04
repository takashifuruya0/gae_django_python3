from google.cloud import datastore
import requests
from django.conf import settings
# logging
import logging
if settings.ENVIRONMENT == "gae":
    logger = logging.getLogger()
else:
    logger = logging.getLogger('django')


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


def apply_dev_to_prod():
    client = datastore.Client()
    query = client.query(kind="PhotoDev")
    photos_dev = list(query.fetch())
    query = client.query(kind="Photo")
    photos_prod = list(query.fetch())
    query = client.query(kind="PhotoBackup")
    photos_buckup = list(query.fetch())
    try:
        # with client.transaction():
        #     print("Transaction start")
        # backup削除
        for photo_backup in photos_buckup:
            print("DELETE {}".format(photo_backup.key))
            client.delete(photo_backup.key)
        # buckup作成
        for photo_prod in photos_prod:
            print("MAKE a backup of {}".format(photo_prod.key))
            key_backup = client.key("PhotoBackup")
            entity = datastore.Entity(key=key_backup)
            for k, v in photo_prod.items():
                entity[k] = v
            client.put(entity)
            client.delete(photo_prod.key)
        # devからprodへ適用
        for photo_dev in photos_dev:
            print("APPLY {} to prod".format(photo_dev.key))
            key = client.key("Photo")
            entity = datastore.Entity(key=key)
            for k, v in photo_dev.items():
                entity[k] = v
            client.put(entity)
        print("Completed applying dev to prod")
        logger.info("Completed applying dev to prod")
        return True
    except Exception as e:
        print("{}".format(e))
        logger.error(e)
        return False
