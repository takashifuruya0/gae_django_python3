from django.shortcuts import render
from django.template.response import TemplateResponse
from google.cloud import datastore

# Create your views here.
def main(request):
    client = datastore.Client()
    query = client.query(kind='Kakeibo')
    data = list(query.fetch())
    output = {
        "msg": "Hello world",
        "data": data,
    }
    return TemplateResponse(request, 'ra/main.html', output)
