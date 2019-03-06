from PIL import Image
from ra.functions import f_datastore
from datetime import datetime
import os
import io
from google.cloud import vision
from google.cloud.vision import types
from google.cloud.datastore.helpers import GeoPoint
import logging
logger = logging.getLogger('django')


def resize_images():
    target = os.listdir('static/image')
    done_resizing = os.listdir('static/image/resized')
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
        # img_resize = img.resize((int(img.width / 3), int(img.height / 3)))
        # update datastore
        # photo.entity['path_resized'] = "image/resized/{}".format(t)
        photo.entity['datetime'] = get_datetime(img)
        photo.update()
    return True


# date
def get_datetime(img):
    exif = img._getexif()
    for id, val in exif.items():
        if id == 36867:
            return datetime(int(val[0:4]), int(val[5:7]), int(val[8:10]))

    return ''


def get_info_by_visionapi():
    # Instantiates a client
    client = vision.ImageAnnotatorClient()
    # target
    target = os.listdir('static/image')
    target.remove("resized")
    for t in target:
        # entity
        photo = f_datastore.Photo().filter("path", "=", "image/{}".format(t)).get_entity()
        # api call履歴がない場合のみ実行
        if not photo.entity.get('is_api_called'):
            # Loads the image into memory
            file_name = "static/image/{}".format(t)
            with io.open(file_name, 'rb') as image_file:
                content = image_file.read()
            image = types.Image(content=content)
            # Performs label detection on the image file
            logger.info("calling Vision API with {}".format(t))
            try:
                response = client.landmark_detection(image=image)
                logger.info("API was called successfully with {}".format(t))
            except Exception as e:
                logger.error("API call was failed with {}".format(t))
                logger.error(e)
            # update entity
            try:
                annotation = response.landmark_annotations
                photo.entity['is_api_called'] = True
                if annotation:
                    photo.entity['landmark'] = annotation[0].description
                    photo.entity['score'] = annotation[0].score
                    photo.entity['location'] = GeoPoint(
                        annotation[0].locations[0].lat_lng.latitude,
                        annotation[0].locations[0].lat_lng.longitude
                    )
                else:
                    photo.entity['landmark'] = None
                photo.client.put(photo.entity)
                logger.info("Updated entity successfully with {}".format(t))
            except Exception as e:
                logger.error("Updating entity was failed with {}".format(t))
                logger.error(e)
                logger.error(annotation)
    return True
    # {
    #     mid: "/m/0415qbd"
    #     description: "Florence"
    #     score: 0.35203754901885986
    #     bounding_poly {
    #         vertices {
    #             x: 75
    #             y: 199
    #         }
    #         vertices {
    #             x: 1443
    #             y: 199
    #         }
    #         vertices {
    #             x: 1443
    #             y: 438
    #         }
    #         vertices {
    #             x: 75
    #             y: 438
    #         }
    #     }
    #     locations {
    #         lat_lng {
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
