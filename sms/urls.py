__author__ = 'thomassaunders'

from django.conf.urls import patterns, include, url
from sms import views


urlpatterns = patterns('',
    url(r'^$', views.home),
    url(r'^send/$',views.send_sms),
    url(r'^(?P<sms_id>\w+)/update/$', views.update_sms_internal)
)