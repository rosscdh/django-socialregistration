from django.conf import settings
from django.conf.urls.defaults import *
from django.views.generic.simple import direct_to_template
from socialregistration.contrib.linkedin_js.views import LinkedInRedirect, \
    LinkedInCallback, LinkedInSetup
 
urlpatterns = patterns('',
    url('^channel\.html$', direct_to_template, {'template':'socialregistration/linkedin_js/channel.html'}, name='channel'),
    url('^callback/$', LinkedInCallback.as_view(), name='callback'),
    url('^setup/$', LinkedInSetup.as_view(), name='setup'),
)
