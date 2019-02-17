from django.template.response import TemplateResponse
from google.cloud import datastore
from ra.functions import f_datastore

# Create your views here.
def main(request):
    # client = datastore.Client()
    # query = client.query(kind='Kakeibo')
    # query.order = ["-date"]
    # data = list(query.fetch(10))
    fds = f_datastore.fds("Kakeibo")
    data = fds.all().order("-date").get()[0:10]
    output = {
        "msg": "Hello world",
        "data": data,
    }
    return TemplateResponse(request, 'ra/main.html', output)
