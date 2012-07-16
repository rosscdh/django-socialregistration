from django.conf import settings
from django.conf.urls.defaults import *
from django.views.generic.simple import direct_to_template
from socialregistration.contrib.facebook.views import FacebookSetup, \
    FacebookRedirect, FacebookCallback
 
urlpatterns = patterns('',
    url('^channel\.html$', direct_to_template, {'template':'socialregistration/facebook_js/channel.html'}, name='channel'),
    url('^redirect/$', FacebookRedirect.as_view(), name='redirect'),
    url('^callback/$', FacebookCallback.as_view(), name='callback'),
    url('^setup/$', FacebookSetup.as_view(), name='setup'),
)
