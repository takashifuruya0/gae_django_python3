from django.template.response import TemplateResponse
from django.shortcuts import HttpResponse, Http404, redirect
from datetime import datetime
from django.conf import settings
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
def top(request):
    photos = f_datastore.Photo().get_list()
    bg_photo = random.choice(photos)
    output = {
        "text": "Hello world",
        "bg_photo": bg_photo,
    }
    return TemplateResponse(request, 'ra/top.html', output)


def ajax(request):
    if request.method in ('POST', "GET"):
        target_properties = ("prefecture", "country", "sitename")
        # GET
        prop = request.GET.get('prop', None)
        text = request.GET.get('text', None)
        labels = [{"key": prop, "val": text}, ]
        if prop and text and prop in target_properties:
            photo = f_datastore.Photo().filter(prop, "=", text).get_list()
            logger.info("ajax:parameter prop={} text={}".format(prop, text))
        else:
            photo = f_datastore.Photo().get_list()
            logger.info("ajax:without parameter")
        # Word Cloud
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
                if pl['count'] > 0 and not check in labels:
                    wordcloud_list.append(pl)
        # datetimeとlocationがJSONに変換できないので、strで送信
        samples = list()
        for p in photo:
            sample = {"id": p.id}
            for k, v in p.items():
                if k == "datetime":
                    sample[k] = v.__str__()
                elif k == "location":
                    logger.info(v)
                    sample[k] = {
                        "latitude": v.latitude,
                        "longitude": v.longitude,
                    }
                    logger.info(sample[k])
                else:
                    sample[k] = v
            samples.append(sample)
        # sampleは24件取得
        samples = random.sample(samples, 24) if len(samples) > 24 else samples

        # データ数が少ないとwcがうまくいかない→数を増やす
        while True:
            if len(wordcloud_list) > 30:
                break
            else:
                wordcloud_list += wordcloud_list
        # property list
        for tp in target_properties:
            property_list[tp] = list(property_list[tp].values())
            property_list[tp].sort(key=lambda x: x['count'], reverse=True)
        # response in JSON
        res_data = {
            "wordcloud_list": wordcloud_list,
            "samples": samples,
            "label": labels[0]['val'],
            "property_list": property_list,
        }
        response = json.dumps(res_data)  # JSON形式に直して・・
        return HttpResponse(response, content_type="text/javascript")  # 返す。JSONはjavascript扱いなのか・・
    else:
        raise Http404


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
            if pl['count'] > 0 and not check in labels:
                wordcloud_list.append(pl)

    # sampling
    photo = random.sample(photo, 24) if len(photo) > 24 else photo
    while True:
        if len(wordcloud_list) > 30:
            break
        else:
            wordcloud_list += wordcloud_list
    for tp in target_properties:
        property_list[tp] = list(property_list[tp].values())
        property_list[tp].sort(key=lambda x: x['count'], reverse=True)
    output = {
        "photo": photo,
        "label": labels[0]['val'] if labels else "",
        "title": "Where to Visit ?",
        "today": datetime.today(),
        "wordcloud_list": wordcloud_list,
        "property_list": property_list,
        "environment": settings.ENVIRONMENT,
    }
    return TemplateResponse(request, "ra/photo.html", output)


@access_time.measure
def photo_edit(request, id):
    if settings.ENVIRONMENT == "local":
        photo = f_datastore.Photo().get_entity_by_id(id)
        if request.method == "GET":
            initial = dict()
            for k, v in photo.entity.items():
                initial[k] = v
            form = PhotoForm(initial=initial)
            output = {
                "form": form,
                "photo": photo.entity,
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
    else:
        raise Http404


@access_time.measure
def photo_detail(request, id):
    photo_data = dict()
    photo_geocoding = dict()
    target_properties = (
        # VisionAPI
        "location", "landmark", "score",
        # geocodingAPI
        "formatted_address",
        "country_en",
        "administrative_area_level_1",
        "administrative_area_level_2",
        "locality", "sublocality",
        "route", "premise",
        # geoAPI
        "city", "town",
        # Input
        "country", "prefecture", "sitename", "comment", "path", "url_origin",
        "datetime",
    )
    # entity
    photo = f_datastore.Photo().get_entity_by_id(id)
    for k, v in photo.entity.items():
        if k in target_properties and v:
            photo_data[k] = v
    if photo.entity.get('landmark'):
        close_places = f_datastore.Photo().filter("locality", "=", photo.entity.get('locality')).get_list()
    else:
        close_places = f_datastore.Photo().filter("prefecture", "=", photo.entity.get('prefecture')).get_list()
    output = {
        "photo": photo_data,
        "close_places": close_places,
        "score_percent": photo.entity.get('score', 0) * 100
    }
    return TemplateResponse(request, 'ra/photo_detail.html', output)

# ============================================================
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
