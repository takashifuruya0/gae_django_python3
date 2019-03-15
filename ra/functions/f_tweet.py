import json
from google.cloud import datastore, storage
from requests_oauthlib import OAuth1Session
from django.conf import settings
import random
import logging
logger = logging.getLogger('django')


def tweet(message, image):
    twitter = OAuth1Session(
        settings.SECRET['TWITTER_CONSUMER_KEY'],
        settings.SECRET['TWITTER_CONSUMER_SECRET'],
        settings.SECRET['TWITTER_ACCESS_KEY'],
        settings.SECRET['TWITTER_ACCESS_SECRET']
    )
    # 画像投稿
    url_media = "https://upload.twitter.com/1.1/media/upload.json"
    files = {"media": image}
    req_media = twitter.post(url_media, files=files)
    if req_media.status_code != 200:
        logger.error("画像アップデート失敗: {}".format(req_media.text))
        return False
    # media ID
    media_id = json.loads(req_media.text)['media_id']
    logger.info("Media ID: {}".format(media_id))
    # テキスト投稿
    url_text = "https://api.twitter.com/1.1/statuses/update.json"
    params = {'status': message, "media_ids": [media_id]}
    req_text = twitter.post(url_text, params=params)
    # レスポンス確認
    if req_text.status_code != 200:
        logger.error("テキストアップデート失敗: {}".format(req_text.text))
        return False
    return True


def test():
    image = open('/Users/furuya/Desktop/DSC06039.jpg', 'rb')
    message = "画像投稿テスト #test #テスト"
    tweet(message, image)


def daily_post():
    # message
    client_datastore = datastore.Client()
    query = client_datastore.query(kind="Photo")
    photos = list(query.fetch())
    photo = random.choice(photos)
    target_properties = (
        # VisionAPI
        "landmark",
        # geocodingAPI
        "country_en",
        "administrative_area_level_1",
        "administrative_area_level_2",
        "locality", "sublocality", "route", "premise",
        # geoAPI
        "city", "town",
        # Input
        "country", "prefecture", "sitename",
    )
    tags = "#旅 #travel #WhereToVisit? "
    for tp in target_properties:
        tag = photo.get(tp, None)
        if tag:
            tags += "#{} ".format(tag)
    url = "https://gae2.fk-management.com/photo/detail/{}".format(photo.id)
    if photo.get("landmark", None):
        landmark = photo.get("landmark", None)
    else:
        landmark = photo.get("sitename", None)
    message = "【{}】 {} {}".format(landmark, tags, url)

    # image
    client_storage = storage.Client()
    bucket = client_storage.get_bucket(settings.SECRET['PROJECT_NAME'])
    blob_name = photo['url_resized_1200'].split("{}/".format(settings.SECRET['PROJECT_NAME']))[1]
    blob = bucket.get_blob(blob_name)
    image = blob.download_as_string()

    # tweet
    tweet(message=message, image=image)


