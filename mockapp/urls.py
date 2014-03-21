__author__ = 'thomassaunders'

from django.conf.urls import patterns, url
from mockapp import views


urlpatterns = patterns('',
    url(r'^$', views.home),
    url(r'^sms/received/$',views.sms_received),
    url(r'^sms/sent/$', views.sms_sent)
)