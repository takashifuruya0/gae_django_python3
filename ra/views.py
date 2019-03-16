from django.template.response import TemplateResponse
from django.shortcuts import HttpResponse, Http404, redirect
from django.conf import settings
import logging
logger = logging.getLogger('django')
from google.cloud import datastore
from ra.form import PhotoForm
from django.contrib import messages
import json
import random
from ra.functions import access_time, f_images


# Create your views here.
@access_time.measure
def top(request):
    client = datastore.Client()
    photos = list(client.query(kind=settings.DATASTORE_KIND).fetch())
    bg_photo = random.choice(photos)
    output = {
        "text": "Hello world",
        "bg_photo": bg_photo,
    }
    return TemplateResponse(request, 'ra/top.html', output)


def ajax(request):
    client = datastore.Client()
    if request.method in ('POST', "GET"):
        target_properties = (
            "prefecture", "country", "sitename", "country_en", "landmark", "locality"
        )
        # GET
        prop = request.GET.get('prop', None)
        text = request.GET.get('text', None)
        labels = [{"key": prop, "val": text}, ]
        if prop and text and prop in target_properties:
            query = client.query(kind=settings.DATASTORE_KIND)
            query.add_filter(prop, "=", text)
            photo = list(query.fetch())
            logger.info("ajax:parameter prop={} text={}".format(prop, text))
        else:
            photo = list(client.query(kind=settings.DATASTORE_KIND).fetch())
            logger.info("ajax:without parameter")
        # Word Cloud
        wordcloud_list = list()
        property_list = dict()
        for tp in target_properties:
            query = client.query(kind=settings.DATASTORE_KIND)
            query.distinct_on = tp
            property_list[tp] = {
                f[tp]: {
                    "word": f[tp],
                    "property": tp,
                    "count": 0,
                    "url": "?{0}={1}".format(tp, f[tp])
                } for f in list(query.fetch())
            }
        for p in photo:
            for tp in target_properties:
                if p.get(tp, None):
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
    output = {
        "title": "Where to Visit ?",
        "environment": settings.ENVIRONMENT,
    }
    return TemplateResponse(request, "ra/photo.html", output)


@access_time.measure
def photo_edit(request, id):
    client = datastore.Client()
    if settings.ENVIRONMENT == "local":
        key = client.key(settings.DATASTORE_KIND, int(id))
        photo = client.get(key=key)
        if request.method == "GET":
            initial = dict()
            # for k, v in photo.entity.items():
            for k, v in photo.items():
                initial[k] = v
            form = PhotoForm(initial=initial)
            output = {
                "form": form,
                "photo": photo,
            }
            logger.info(output)
            return TemplateResponse(request, 'ra/photo_edit.html', output)
        elif request.method == "POST":
            form = PhotoForm(request.POST)
            form.is_valid()
            post_data = form.cleaned_data
            for i in photo.keys():
                # photo.entity[i] = post_data.get(i)
                photo[i] = post_data.get(i, photo[i])
            # photo.update()
            client.put(photo)
            # messages.success(request, "{} was updated".format(photo.entity.id))
            # logger.info("{} was updated".format(photo.entity.id))
            messages.success(request, "{} was updated".format(photo.id))
            logger.info("{} was updated".format(photo.id))
            return redirect('ra:photo')
    else:
        raise Http404


@access_time.measure
def photo_detail(request, id):
    photo_data = dict()
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
    client = datastore.Client()
    key = client.key(settings.DATASTORE_KIND, int(id))
    photo = client.get(key=key)
    for k, v in photo.items():
        if k in target_properties and v:
            photo_data[k] = v
    # close places
    query = client.query(kind=settings.DATASTORE_KIND)
    if photo.get('landmark'):
        query.add_filter("locality", "=", photo.get('locality'))
    else:
        query.add_filter("prefecture", "=", photo.get('prefecture'))
    close_places = list(query.fetch())
    # return
    output = {
        "photo": photo_data,
        "close_places": close_places,
        "score_percent": photo.get('score', 0) * 100
    }
    return TemplateResponse(request, 'ra/photo_detail.html', output)


# f_images.create_entity_of_new_photos()を実行
def process_create(request):
    if request.POST.get("token") == settings.SECRET['TOKEN_PROCESS_CREATE']:
        try:
            logger.info("f_images.create_entity_of_new_photo() is called via HTTP request.")
            result = f_images.create_entity_of_new_photo(request.POST.get('blob_name'))
            logger.info("f_images.create_entity_of_new_photo() is completed")
        except Exception as e:
            logger.error(e)
            raise Http404
    else:
        result = False
    res_data = {
        "result": result
    }
    response = json.dumps(res_data)  # JSON形式に直して・・
    return HttpResponse(response, content_type="text/javascript")  # 返す。JSONはjavascript扱いなのか・