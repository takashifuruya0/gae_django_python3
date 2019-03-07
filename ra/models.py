from django.db import models
from django.contrib.auth.models import User
from django.contrib.postgres.fields import ArrayField


# Create your models here.
class habit(models.Model):
    date = models.DateField()
    name = models.CharField(max_length=30)
    user = models.ForeignKey(User, on_delete=models.PROTECT)

    def __str__(self):
        return self.name


class Photo(models.Model):
    comment = models.CharField(max_length=100, blank=True)
    sitename = models.CharField(max_length=100, blank=True)
    prefecture = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=100)
    path = models.CharField(max_length=100)
    path_resized = models.CharField(max_length=100)
    path_resized_480 = models.CharField(max_length=100)
    path_resized_1200 = models.CharField(max_length=100)
    datetime = models.DateTimeField()
    landmark = models.CharField(max_length=100, blank=True)
    latitude = models.FloatField(blank=True)
    longitude = models.FloatField(blank=True)
    score = models.FloatField(blank=True)
    is_api_called = models.BooleanField(default=False)
    tags = ArrayField(models.CharField(max_length=100), blank=True)
