from django.template.response import TemplateResponse
from django.shortcuts import HttpResponse, Http404, redirect
# from google.cloud import datastore
from datetime import datetime
import logging
from ra.functions import f_datastore
from ra.form import FmanageForm, TrainingForm
from django.contrib import messages
import json


# Create your views here.
def main(request):
    if request.method == "GET":
        form = FmanageForm(initial={"datetime": datetime.today()})
        fds = f_datastore.fds("fmanage")
        data = fds.all().order("-datetime").get(10)
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
        fds = f_datastore.fds("fmanage")
        fds.data = {
            "name": post_data.get("name"),
            "age": post_data.get("age"),
            "datetime": post_data.get("datetime"),
        }
        if fds.create():
            messages.success(request, "Saved")
        else:
            messages.error(request, "Failed")
            logging.error("Failed")
        return redirect("ra:main")


def ajax(request):
    if request.method in ('POST', "GET"):
        data = {
            'your_surprise_txt': "surprise_txt",
        }
        response = json.dumps(data)  # JSON形式に直して・・
        return HttpResponse(response, content_type="text/javascript")  # 返す。JSONはjavascript扱いなのか・・
    else:
        raise Http404  # GETリクエストを404扱いにしているが、実際は別にしなくてもいいかも

def training(request):
    if request.method == "POST":
        return redirect('ra:training')
    elif request.method == "GET":
        form = TrainingForm(initial={"datetime": datetime.today(), "no_set": 3,})
        output = {
            "form": form,
        }
        return TemplateResponse(request, "ra/training.html", output)
