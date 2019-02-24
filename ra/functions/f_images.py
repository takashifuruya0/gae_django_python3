from PIL import Image
from ra.functions import f_datastore
import os


def resize_images():
    target = os.listdir('static/image')
    done_resizing = os.listdir('static/image/resized')
    target.remove("resized")
    for t in target:
        if not t in done_resizing:
            # resize
            img = Image.open("static/image/{}".format(t))
            img_resize = img.resize((int(img.width / 3), int(img.height / 3)))
            img_resize.save("static/image/resized/{}".format(t))
            # update datastore
            photo = f_datastore.Photo().filter("path", "=", "image/{}".format(t)).get_entity()
            photo.entity['path_resized'] = "image/resized/{}".format(t)
            photo.update()
    return True
