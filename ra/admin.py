from django.contrib import admin
from .models import *
# Register your models here.


class habitAdmin(admin.ModelAdmin):
    list_display = ['pk', 'date', 'name', 'user']


admin.site.register(habit, habitAdmin)
