from django.conf.urls import patterns, include, url
from Web.views import pnf
from Web.views import ise

urlpatterns = patterns('',
    url(r'^', include('Web.urls')),
)

handler404 = pnf
handler500 = ise
