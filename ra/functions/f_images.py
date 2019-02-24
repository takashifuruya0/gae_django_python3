from PIL import Image
from ra.functions import f_datastore
from datetime import datetime
import os


def resize_images():
    target = os.listdir('static/image')
    done_resizing = os.listdir('static/image/resized')
    target.remove("resized")
    for t in target:
        # if not t in done_resizing:
        print(t)
        # resize
        img = Image.open("static/image/{}".format(t))
        img_resize = img.resize((int(img.width / 3), int(img.height / 3)))
        img_resize.save("static/image/resized/{}".format(t))
        # update datastore
        photo = f_datastore.Photo().filter("path", "=", "image/{}".format(t)).get_entity()
        photo.entity['path_resized'] = "image/resized/{}".format(t)
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
