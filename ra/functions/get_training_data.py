import requests
from datetime import datetime
from google.cloud import datastore


def save_to_datastore():
    client = datastore.Client()
    key = datastore.key("Training")
    url = 'https://script.google.com/macros/s/AKfycbzzdezErfyIDi_byfVKvEQqpgYt6-Lq4-rMUmXwyU2RkdyAhX8/exec'
    r = requests.get(url)
    data_list = r.json()['data_list']
    for d in data_list:
        d['datetime'] = datetime(int(d['datetime'][0:4]), int(d['datetime'][5:7]), int(d['datetime'][8:10]))
        t = datastore.Entity(key)
        t.update(d)
        client.put(t)
