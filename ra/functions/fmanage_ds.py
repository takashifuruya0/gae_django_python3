from google.cloud import datastore
from datetime import datetime
import logging

class fmanage():
    client = None
    key = None
    kind = None

    def __init__(self):
        self.client = datastore.Client()
        self.kind = "fmanage"
        self.key = self.client.key(self.kind)

    def get(self):
        query = self.client.query(kind=self.kind)
        return list(query.fetch())

    def create(self, data=None):
        entity = datastore.Entity(key=self.key)
        if not data:
            data = {
                "datetime": datetime.today(),
                "name": "Furuya",
                "age": 26,
            }
        # for k, v in data.items():
        #     entity[k] = v
        try:
            entity.update(data)
            self.client.put(entity)
            return True
        except Exception as e:
            logging.error(e)
            return False
