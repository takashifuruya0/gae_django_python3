from django.template.response import TemplateResponse
from django.shortcuts import HttpResponse, Http404, redirect
# from google.cloud import datastore
from datetime import datetime
import logging
logger = logging.getLogger('django')
from ra.functions import f_datastore
from ra.form import FmanageForm, TrainingForm, PhotoForm
from django.contrib import messages
import json
import random
from ra.functions import access_time


# Create your views here.
@access_time.measure
def main(request):
    if request.method == "GET":
        form = FmanageForm(initial={"datetime": datetime.today()})
        fds = f_datastore.Fds("fmanage")
        data = fds.order("-datetime").get_list(10)
        output = {
            "msg": "Hello world",
            "data": data,
            "form": form,
            "today": datetime.today()
        }
        return TemplateResponse(request, 'ra/main.html', output)
    elif request.method == "POST":
        form = FmanageForm(request.POST)
        form.is_valid()
        post_data = form.cleaned_data
        fds = f_datastore.Fds("fmanage")
        fds.data = {
            "name": post_data.get("name"),
            "age": post_data.gett("age"),
            "datetime": post_data.get("datetime"),
        }
        if fds.create():
            messages.success(request, "Saved")
        else:
            messages.error(request, "Failed")
            logger.error("Failed")
        return redirect("ra:main")


def ajax(request):
    if request.method in ('POST', "GET"):
        # data = {
        #     'your_surprise_txt': "The number of training: {}".format(f_datastore.Training().get_list().__len__()),
        # }
        target_properties = ("prefecture", "country", "sitename")
        # GET
        prop = request.GET.get('prop')
        text = request.GET.get('text')
        logger.info("ajax:parameter prop={} text={}".format(prop, text))
        # Word Cloud
        photo = f_datastore.Photo().filter(prop, "=", text).get_list()
        wordcloud_list = list()
        propery_list = dict()
        label_check = [{"key": prop, "val": text}, ]
        for tp in target_properties:
            propery_list[tp] = {
                f[tp]: {
                    "word": f[tp],
                    "property": tp,
                    "count": 0,
                    "url": "?{0}={1}".format(tp, f[tp])
                } for f in f_datastore.Photo().distinct(tp).get_list()
            }
        for p in photo:
            for tp in target_properties:
                propery_list[tp][p[tp]]['count'] += 1
        for pls in propery_list.values():
            for key, pl in pls.items():
                check = {
                    "key": pl["property"],
                    "val": pl['word']
                }
                if pl['count'] > 0 and not check in label_check:
                    wordcloud_list.append(pl)
        samples = list()
        for p in photo:
            sample = {"id": p.id}
            for k, v in p.items():
                val = v.__str__() if k in ("datetime", "location") else v
                sample[k] = val
            samples.append(sample)
        res_data = {
            "wordcloud_list": wordcloud_list,
            "samples": samples,
        }
        response = json.dumps(res_data)  # JSON形式に直して・・
        return HttpResponse(response, content_type="text/javascript")  # 返す。JSONはjavascript扱いなのか・・
    else:
        raise Http404


@access_time.measure
def wordcloud(request):
    testdata = [
        {"word": "イノシシ", "count": 9, "url": "/photo/"},
        {"word": "おにやんま", "count": 3, "url": "/photo/"},
        {"word": "ゆるっと", "count": 4, "url": "/photo/"},
        {"word": "映画", "count": 3, "url": "/photo/"},
        {"word": "河津桜", "count": 2, "url": "/photo/"},
        {"word": "ふるや", "count": 10, "url": "/photo/"},
    ]
    return TemplateResponse(request, 'ra/wordcloud.html', {'testdata': testdata})


@access_time.measure
def training(request):
    if request.method == "POST":
        form = TrainingForm(request.POST)
        form.is_valid()
        post_data = form.cleaned_data
        fds = f_datastore.Fds("Training")
        fds.data = {
            "name": post_data.get("name"),
            "weight": post_data.get("weight"),
            "set": post_data.get("set"),
            "datetime": post_data.get("datetime"),
        }
        if fds.create():
            messages.success(request, "Saved")
        else:
            messages.error(request, "Failed")
            logger.error("Failed")
        return redirect('ra:training')
    elif request.method == "GET":
        # GETパラメータ
        name_chart = request.GET.get("name", "レッグプレス")
        # form
        form = TrainingForm(initial={"datetime": datetime.today(), "set": 3, })
        # datastore
        training_data = f_datastore.Fds("Training")
        res = list()
        data = training_data.order("-datetime").get_list()
        for d in training_data.filter("name", "=", name_chart).order("-datetime").get_list():
            tmp = {
                "datetime": d['datetime'],
                "weight": d['weight'],
                "set": d['set']
            }
            res.append(tmp)
        output = {
            "today": datetime.today(),
            "form": form,
            "data": data,
            "length": data.__len__(),
            "data_chart": res,
            "name_chart": name_chart,
            "length_chart": res.__len__(),
        }
        logger.info(output)
        return TemplateResponse(request, "ra/training.html", output)


@access_time.measure
def photo(request):
    labels = list()
    target_properties = ("prefecture", "country", "sitename")
    for f in target_properties:
        param = request.GET.get(f, None)
        if param:
            labels.append({
                "key": f,
                "val": param,
            })
            photo = f_datastore.Photo().filter(f, "=", param).get_list()
            break
        else:
            photo = f_datastore.Photo().get_list()
    # wordcloud
    label_check = (l['val'] for l in labels)
    wordcloud_list = list()
    property_list = dict()
    for tp in target_properties:
        property_list[tp] = {
            f[tp]: {
                "word": f[tp],
                "property": tp,
                "count": 0,
                "url": "?{0}={1}".format(tp, f[tp])
            } for f in f_datastore.Photo().distinct(tp).get_list()
        }
    for p in photo:
        for tp in target_properties:
            property_list[tp][p[tp]]['count'] += 1
    for pls in property_list.values():
        for pl in pls.values():
            check = {
                "key": pl["property"],
                "val": pl['word']
            }
            if pl['count'] > 0 and not check in label_check:
                wordcloud_list.append(pl)

    # sampling
    photo = random.sample(photo, 20) if len(photo) > 20 else photo
    # for tp in target_properties:
    #     property_list[tp] = {
    #         f[tp]: {
    #             "word": f[tp],
    #             "property": tp,
    #             "url_param": "?{0}={1}".format(tp, f[tp])
    #         } for f in photo
    #     }
    output = {
        "photo": photo,
        "labels": labels,
        "title": "Find where you wanna visit !",
        "today": datetime.today(),
        "wordcloud_list": wordcloud_list,
        "property_list": property_list,
    }
    logger.info(output)
    return TemplateResponse(request, "ra/photo.html", output)


@access_time.measure
def photo_edit(request, id):
    photo = f_datastore.Photo().get_entity_by_id(id)
    if request.method == "GET":
        initial = dict()
        for k, v in photo.entity.items():
            initial[k] = v
        form = PhotoForm(initial=initial)
        output = {
            "form": form,
            "path": initial['path']
        }
        logger.info(output)
        return TemplateResponse(request, 'ra/photo_edit.html', output)
    elif request.method == "POST":
        form = PhotoForm(request.POST)
        form.is_valid()
        post_data = form.cleaned_data
        for i in photo.data.keys():
            photo.entity[i] = post_data.get(i)
        photo.update()
        messages.success(request, "{} was updated".format(photo.entity.id))
        logger.info("{} was updated".format(photo.entity.id))
        return redirect('ra:photo')
