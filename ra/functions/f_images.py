from PIL import Image
from datetime import datetime
import io
from google.cloud import vision
from google.cloud.vision import types
from google.cloud import datastore
from google.cloud.datastore.helpers import GeoPoint
from google.cloud import storage
from google.cloud.storage import Blob
import googlemaps
import requests
from django.conf import settings
from ra.functions import f_lib
import logging
if settings.ENVIRONMENT == "gae":
    logger = logging.getLogger()
else:
    logger = logging.getLogger('django')


# to_be_processed/に格納されている写真に対して、create_entity_of_new_photoを実行
def create_entity_of_new_photos():
    # storage
    client_storage = storage.Client()
    bucket = client_storage.get_bucket(settings.SECRET['PROJECT_NAME'])
    target = list(bucket.list_blobs(prefix="to_be_processed/"))[1:]
    for t in target:
        create_entity_of_new_photo(t.name)
    return True


# imgから撮影日時を取得
def get_datetime(img):
    exif = img._getexif()
    for id, val in exif.items():
        if id == 36867:
            return datetime(int(val[0:4]), int(val[5:7]), int(val[8:10]))
    return None


# Google Maps Geocoding APIから情報取得
def get_info_by_geocodingapi(latitude, longitude):
    gmaps = googlemaps.Client(key=settings.GOOGLE_MAPS_API_KEY)
    result = gmaps.reverse_geocode((latitude, longitude))
    types = (
        'premise',  # Ksar d'Aït Ben Haddou"
        "route",  # Unnamed Road
        "sublocality",  # Takashimamachi
        "locality",  # Nagasaki-shi
        'administrative_area_level_2',  # Province de Ouarzazate
        "administrative_area_level_1",  # Nakagasaki-ken
        "country",  # Japan
    )
    res = {t: None for t in types}
    r = result[0]
    res['formatted_address'] = r['formatted_address']
    for ac in r['address_components']:
        for ac_type in ac['types']:
            if ac_type in types:
                res[ac_type] = ac['long_name']
    return res


# geo APIから日本の住所情報を取得
def get_info_by_geoapi(latitude, longitude):
    url = "http://geoapi.heartrails.com/api/json?method=searchByGeoLocation"
    params = {
        "x": longitude,
        "y": latitude
    }
    r = requests.get(url, params=params)
    data = r.json()['response']['location'][0]
    res = {
        "prefecture": data['prefecture'],
        "city": data['city'],
        "town": data['town'],
    }
    return res


# Vision APIからLandmark情報を取得
def get_landmark_by_visionapi(image_data):
    # Instantiates a client
    client = vision.ImageAnnotatorClient()
    # Loads the image into memory
    logger.info("loading image")
    image = types.Image(content=image_data)
    del image_data
    # Performs label detection on the image file
    logger.info("calling Vision API")
    try:
        response = client.landmark_detection(image=image)
        logger.info("API was called successfully")
        if response.landmark_annotations:
            return response.landmark_annotations[0]
        else:
            logger.info("Got no annotation")
            return None
    except Exception as e:
        logger.error("Failed to get annotations")
        logger.error(e)
        return None
    # annotation = {
    #     score: 0.35203754901885986,
    #     description: "Florence",
    #     locations: {
    #         lat_lng: {
    #             latitude: 43.767902
    #             longitude: 11.257285
    #         }
    #     }
    # }

# >>> response_label.label_annotations
# [
#     mid: "/m/01bqvp"
#     description: "Sky"
#     score: 0.9761796593666077
#     topicality: 0.9761796593666077
#     ,
#     mid: "/m/03ktm1"
#     description: "Body of water"
#     score: 0.974838376045227
#     topicality: 0.974838376045227
#     ,
#     mid: "/m/06cnp"
#     description: "River"
#     score: 0.9544249176979065
#     topicality: 0.9544249176979065
#     ,
# ]


# 写真のリサイズ・エンティティ作成・公開・API callを実行
def create_entity_of_new_photo(blob_name):
    # datastore
    client_datastore = datastore.Client()
    # storage
    client_storage = storage.Client()
    bucket = client_storage.get_bucket(settings.SECRET['PROJECT_NAME'])
    t = bucket.get_blob(blob_name)
    # width after resizing
    resize_sizes = (1200, 480)
    # copy target image
    logger.info("Target: {}".format(t.name))
    file_name = t.name.split("/")[1]
    blob_origin = bucket.copy_blob(blob=t, destination_bucket=bucket, new_name="image/{}".format(file_name))
    blob_origin.make_public()
    logger.info("{} is copied to {}".format(t.name, blob_origin.name))
    # resize
    query = client_datastore.query(kind=settings.DATASTORE_KIND)
    query.add_filter("path", "=", blob_origin.name)
    photos = list(query.fetch())
    if not photos:
        # preparing
        img = Image.open(io.BytesIO(t.download_as_string()))
        data = {
            "country": "Check",
            "prefecture": "Check",
            "sitename": "Check",
            "path": blob_origin.name,
            "url_origin": blob_origin.public_url,
            'is_api_called': False,
            'datetime': get_datetime(img),
        }
        # resizing image
        for width_rev in resize_sizes:
            logger.info("Resizing {} to the width of {}".format(blob_origin.name, width_rev))
            height_rev = img.height * width_rev / img.width
            img_resize = img.resize((int(width_rev), int(height_rev)))
            f_name = "resized_{}/{}".format(width_rev, t.name.split("/")[1])
            # BytesIOで一時保存
            bio = io.BytesIO()
            img_resize.save(bio, format='jpeg')
            # Cloud Storageへアップロード
            blob = Blob(f_name, bucket)
            blob.upload_from_string(data=bio.getvalue(), content_type="image/jpeg")
            # 公開設定
            blob.make_public()
            logger.info("Completed resizing {} to the width of {}".format(blob_origin.name, width_rev))
            # 公開URLをdataに格納
            data["url_resized_{}".format(width_rev)] = blob.public_url
        # memory開放
        del bio, img
        # creating entity
        logger.info("Creating entity of {}".format(blob_origin.name))
        entity = datastore.Entity(key=client_datastore.key(settings.DATASTORE_KIND))
        entity.update(data)
        client_datastore.put(entity)
        logger.info("Completed creating entity of {}".format(blob_origin.name))
    # delete target photo
    logger.info("Deleting {}".format(t.name))
    t.delete()
    logger.info("Completed deleting {}".format(t.name))

    # APIでentityをアップデートする
    update_entity_by_api(entity['path'])
    return True


# apiの情報でentityをupdate
def update_entity_by_api(path):
    client_datastore = datastore.Client()
    client_storage = storage.Client()
    bucket = client_storage.get_bucket(settings.SECRET['PROJECT_NAME'])
    query = client_datastore.query(kind=settings.DATASTORE_KIND)
    query.add_filter("path", "=", path)
    photo_query = list(query.fetch())
    if photo_query:
        photo = photo_query[0]
    else:
        return False
    # api call履歴がない場合のみ実行
    if not photo.get('is_api_called'):
        logger.info("The entity of {} will be updated by calling APIs".format(photo.key))
        try:
            blob = bucket.get_blob(photo['path'])
            # VisionAPI
            annotation = get_landmark_by_visionapi(blob.download_as_string())
            photo['is_api_called'] = True
            if annotation:
                photo['landmark'] = annotation.description
                photo['score'] = annotation.score
                photo['location'] = GeoPoint(
                    annotation.locations[0].lat_lng.latitude,
                    annotation.locations[0].lat_lng.longitude
                )
            else:
                photo['landmark'] = None
            client_datastore.put(photo)
            logger.info("Updated entity successfully by Vision API on {}".format(photo.key))
        except Exception as e:
            logger.error("Updating entity by Vision API was failed on {}".format(photo.key))
            logger.error(e)

        if photo['landmark']:
            # geocodingAPI
            # photo['sitename'] = photo['landmark']
            geocode = get_info_by_geocodingapi(
                photo['location'].latitude,
                photo['location'].longitude,
            )
            for k, v in geocode.items():
                k = "country_en" if k is "country" else k
                photo[k] = v
            # 日本語化
            # country
            photo['country'] = f_lib.translate_en_to_ja(photo['country_en'])
            # prefecture
            text = photo['locality'] if photo['locality'] else photo['administrative_area_level_1']
            photo['prefecture'] = f_lib.translate_en_to_ja(text)
            # landmark
            photo['sitename'] = f_lib.translate_en_to_ja(photo['landmark'])
            # update
            client_datastore.put(photo)
            logger.info("Updated entity successfully by Geocoding API on {}".format(photo.key))

            if photo['country'] == "日本" or photo['country_en'] == "Japan":
                # 日本の住所
                photo['country'] = "日本"
                photo['country_en'] = "Japan"
                japanese_address = get_info_by_geoapi(
                    photo['location'].latitude,
                    photo['location'].longitude,
                )
                for k, v in japanese_address.items():
                    photo[k] = v
                client_datastore.put(photo)
                logger.info("Updated entity successfully by geo API on {}".format(photo))
    else:
        logger.info("{} has already called APIs".format(photo.key))
    return True


# ==========================================
#    OLD METHODS
# ==========================================
# apiの情報でentityをupdate
def update_entities_by_api(do_all=False):
    client_datastore = datastore.Client()
    client_storage = storage.Client()
    bucket = client_storage.get_bucket(settings.SECRET['PROJECT_NAME'])
    target_photos = list(client_datastore.query(kind=settings.DATASTORE_KIND).fetch())
    for photo in target_photos:
        # api call履歴がない場合のみ実行
        if not photo.get('is_api_called') or do_all:
            logger.info("The entity of {} will be updated by calling APIs".format(photo.key))
            try:
                blob = bucket.get_blob(photo['path'])
                # VisionAPI
                annotation = get_landmark_by_visionapi(blob.download_as_string())
                photo['is_api_called'] = True
                if annotation:
                    photo['landmark'] = annotation.description
                    photo['score'] = annotation.score
                    photo['location'] = GeoPoint(
                        annotation.locations[0].lat_lng.latitude,
                        annotation.locations[0].lat_lng.longitude
                    )
                else:
                    photo['landmark'] = None
                client_datastore.put(photo)
                logger.info("Updated entity successfully by Vision API on {}".format(photo.key))
            except Exception as e:
                logger.error("Updating entity by Vision API was failed on {}".format(photo.key))
                logger.error(e)

            if photo['landmark']:
                # geocodingAPI
                geocode = get_info_by_geocodingapi(
                    photo['location'].latitude,
                    photo['location'].longitude,
                )
                for k, v in geocode.items():
                    k = "country_en" if k is "country" else k
                    photo[k] = v
                client_datastore.put(photo)
                logger.info("Updated entity successfully by Geocoding API on {}".format(photo.key))

                if photo['country'] == "日本" or photo['country_en'] == "Japan":
                    # 日本の住所
                    photo['country'] = "日本"
                    photo['country_en'] = "Japan"
                    japanese_address = get_info_by_geoapi(
                        photo['location'].latitude,
                        photo['location'].longitude,
                    )
                    for k, v in japanese_address.items():
                        photo[k] = v
                    client_datastore.put(photo)
                    logger.info("Updated entity successfully by geo API on {}".format(photo))
        else:
            logger.info("{} has already called APIs".format(photo.key))
    return True