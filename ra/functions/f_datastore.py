from google.cloud import datastore
from datetime import datetime
import logging

class Fds():
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
        self.query = self.client.query(kind=self.kind)

    def get(self, num=None):
        if num:
            return list(self.query.fetch(num))
        else:
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

    def distinct(self, property):
        self.query.distinct_on = [property]
        return self

    def update(self):
        self.put(self.entity)
        return self.entity


class Test(Fds):
    kind = "Test"
    data = {
        "name": None,
        "age": None,
        "datetime": None,
    }

    def __init__(self):
        super().__init__(self.kind)


class Training(Fds):
    kind = "Training"
    data = {
        "name": None,
        "set": None,
        "weight": None,
        "datetime": None,
    }

    def __init__(self):
        super().__init__(self.kind)


class Photo(Fds):
    kind = "Photo"
    data = {
        "comment": None,
        "sitename": None,
        "prefecture": None,
        "country": None,
        "path": None,
        "datetime": None
    }

    def __init__(self):
        super().__init__(self.kind)