from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class habit(models.Model):
    date = models.DateField()
    name = models.CharField(max_length=30)
    user = models.ForeignKey(User, on_delete=models.PROTECT)

    def __str__(self):
        return self.name

