from PIL import Image
from ra.functions import f_datastore
import os


def resize_images():
    target = os.listdir('static/image').remove("resized")
    for t in target:
        # resize
        img = Image.open("static/image/{}".format(t))
        img_resize = img.resize((int(img.width / 3), int(img.height / 3)))
        img_resize.save("static/image/resized/{}".format(t))
        # update datastore
        photo = f_datastore.Photo().filter("path", "=", "static/image/{}".format(t))
        photo.data['path_resized'] = "static/image/resized/{}".format(t)
        photo.update()
