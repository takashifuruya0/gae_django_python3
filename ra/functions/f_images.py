from PIL import Image
from ra.functions import f_datastore
from datetime import datetime
import os
import io
from google.cloud import vision
from google.cloud.vision import types
from google.cloud.datastore.helpers import GeoPoint
import googlemaps
import requests
from django.conf import settings
import logging
logger = logging.getLogger('django')


def resize_images():
    target = os.listdir('static/image')
    target.remove("resized")
    for t in target:
        # resize
        img = Image.open("static/image/{}".format(t))
        photo = f_datastore.Photo().filter("path", "=", "image/{}".format(t)).get_entity()
        resize_sizes = (1200, 480)
        for width_rev in resize_sizes:
            height_rev = img.height * width_rev / img.width
            img_resize = img.resize((int(width_rev), int(height_rev)))
            img_resize.save("static/resized_{0}/{1}".format(width_rev, t))
            photo.entity['path_resized_{}'.format(width_rev)] = "resized_{0}/{1}".format(width_rev, t)
        photo.entity['datetime'] = get_datetime(img)
        photo.update()
    return True


# imgから撮影日時を取得
def get_datetime(img):
    exif = img._getexif()
    for id, val in exif.items():
        if id == 36867:
            return datetime(int(val[0:4]), int(val[5:7]), int(val[8:10]))
    return None


# apiの情報でentityをupdate
def update_entities_by_api(do_all=False):
    # target
    target = os.listdir('static/image')
    target.remove("resized")
    for t in target:
        # entity
        photo = f_datastore.Photo().filter("path", "=", "image/{}".format(t)).get_entity()
        # api call履歴がない場合のみ実行
        if not photo.entity.get('is_api_called') or do_all:
            try:
                # VisionAPI
                annotation = get_landmark_by_visionapi(photo.entity['path'])
                photo.entity['is_api_called'] = True
                if annotation:
                    photo.entity['landmark'] = annotation.description
                    photo.entity['score'] = annotation.score
                    photo.entity['location'] = GeoPoint(
                        annotation.locations[0].lat_lng.latitude,
                        annotation.locations[0].lat_lng.longitude
                    )
                else:
                    photo.entity['landmark'] = None
                photo.client.put(photo.entity)
                logger.info("Updated entity successfully by Vision API on {}".format(t))
            except Exception as e:
                logger.error("Updating entity by Vision API was failed on {}".format(t))
                logger.error(e)

            if photo.entity['landmark']:
                # geocodingAPI
                geocode = get_info_by_geocodingapi(
                    photo.entity['location'].latitude,
                    photo.entity['location'].longitude,
                )
                for k, v in geocode.items():
                    k = "country_en" if k is "country" else k
                    photo.entity[k] = v
                photo.client.put(photo.entity)
                logger.info("Updated entity successfully by Geocoding API on {}".format(t))

                if photo.entity['country'] in ("Japan", "日本"):
                    # 日本の住所
                    japanese_address = get_info_by_geoapi(
                        photo.entity['location'].latitude,
                        photo.entity['location'].longitude,
                    )
                    for k, v in japanese_address.items():
                        photo.entity[k] = v
                    photo.client.put(photo.entity)
                    logger.info("Updated entity successfully by geo API on {}".format(t))
    return True


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
def get_landmark_by_visionapi(image_path):
    # Instantiates a client
    client = vision.ImageAnnotatorClient()
    # Loads the image into memory
    logger.info("loading image of {}".format(image_path))
    file_name = "static/{}".format(image_path)
    with io.open(file_name, 'rb') as image_file:
        content = image_file.read()
    image = types.Image(content=content)
    # Performs label detection on the image file
    logger.info("calling Vision API with {}".format(image_path))
    try:
        response = client.landmark_detection(image=image)
        logger.info("API was called successfully with {}".format(image_path))
        if response.landmark_annotations:
            return response.landmark_annotations[0]
        else:
            logger.info("Got no annotation from {}".format(image_path))
            return None
    except Exception as e:
        logger.error("Failed to get annotations of {}".format(image_path))
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
#     mid: "/m/05h0n"
#     description: "Nature"
#     score: 0.9494227766990662
#     topicality: 0.9494227766990662
#     ,
#     mid: "/m/0838f"
#     description: "Water"
#     score: 0.9388793110847473
#     topicality: 0.9388793110847473
#     ,
#     mid: "/m/02l215"
#     description: "Reflection"
#     score: 0.9338679313659668
#     topicality: 0.9338679313659668
#     ,
#     mid: "/m/01b2w5"
#     description: "Sunset"
#     score: 0.9231336116790771
#     topicality: 0.9231336116790771
#     ,
#     mid: "/m/015kr"
#     description: "Bridge"
#     score: 0.9136024117469788
#     topicality: 0.9136024117469788
#     ,
#     mid: "/m/013vs"
#     description: "Afterglow"
#     score: 0.9109726548194885
#     topicality: 0.9109726548194885
#     ,
#     mid: "/m/01b3l7"
#     description: "Dusk"
#     score: 0.8954203128814697
#     topicality: 0.8954203128814697
# ]