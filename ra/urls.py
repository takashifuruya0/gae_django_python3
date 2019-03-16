from django.conf.urls import url
from . import views

app_name = 'ra'

urlpatterns = [
    # url(r'^$', views.main, name='main'),
    # url(r'^wordcloud/$', views.wordcloud, name='wordcloud'),
    # url(r'^training/$', views.training, name='training'),
    url(r'^$', views.top, name='main'),
    url(r'^ajax/$', views.ajax, name='ajax'),
    url(r'^photo/$', views.photo, name='photo'),
    url(r'^photo/detail/(?P<id>\d+)/edit/$', views.photo_edit, name='photo_edit'),
    url(r'^photo/detail/(?P<id>\d+)/$', views.photo_detail, name='photo_detail'),
    url(r'^photo/process/create/$', views.process_create, name='process_create'),
]