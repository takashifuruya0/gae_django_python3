from google.cloud import datastore
from datetime import datetime
import logging

class fds():
    client = None
    key = None
    query = None
    kind = None
    entity = None
    data = None

    def __init__(self, kind):
        self.client = datastore.Client()
        self.kind = kind
        self.key = self.client.key(self.kind)

    def get(self):
        return list(self.query.fetch())

    def all(self):
        self.query = self.client.query(kind=self.kind)
        return self

    def create(self):
        self.entity = datastore.Entity(key=self.key)
        self.entity.update(self.data)
        self.client.put(self.entity)
        return self.entity

    def filter(self, property, operation, value):
        self.query.add_filter(property, operation, value)
        return self

    def order(self, property):
        self.query.order = [property]
        return self


class test(fds):
    data = {
        "name": None,
        "age": None,
        "datetime": None,
    }