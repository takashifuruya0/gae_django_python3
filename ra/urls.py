from django.conf.urls import url
from . import views

app_name = 'ra'

urlpatterns = [
    # url(r'^$', views.main, name='main'),
    url(r'^$', views.top, name='main'),
    url(r'^ajax/$', views.ajax, name='ajax'),
    # url(r'^wordcloud/$', views.wordcloud, name='wordcloud'),
    # url(r'^training/$', views.training, name='training'),
    url(r'^photo/$', views.photo, name='photo'),
    url(r'^photo/edit/(?P<id>\d+)/$', views.photo_edit, name='photo_edit'),
]