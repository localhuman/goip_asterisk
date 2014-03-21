from django.conf.urls import patterns, include, url
from django.contrib import admin
from asterisk.views import home
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', home),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^sms/', include('sms.urls')),
    url(r'^mock/', include('mockapp.urls')),
)