from PIL import Image
from ra.functions import f_datastore
from datetime import datetime
import os


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
