from django.conf.urls import url
from . import views

app_name = 'ra'

urlpatterns = [
    url(r'^$', views.main, name='main'),
    url(r'^ajax/$', views.ajax, name='ajax'),
    url(r'^training/$', views.training, name='training')
]