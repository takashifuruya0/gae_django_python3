from django.template.response import TemplateResponse
from django.shortcuts import redirect
# from google.cloud import datastore
from datetime import datetime
import logging
from ra.functions import f_datastore
from ra.form import FmanageForm
from django.contrib import messages


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