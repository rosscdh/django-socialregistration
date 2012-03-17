from django.conf import settings
from django.contrib.sites.models import Site
from django.core.urlresolvers import reverse
from openid.consumer import consumer
from openid.extensions import ax
from socialregistration.clients import Client
from socialregistration.contrib.openid.storage import OpenIDStore
from socialregistration.settings import SESSION_KEY
import urlparse

AX_URLS = getattr(settings, 'SOCIALREGISTRATION_AX_URLS',
    None)

class OpenIDClient(Client):

    def __init__(self, session_data, endpoint_url):
        self.endpoint_url = endpoint_url
        self.store = OpenIDStore()
        self.consumer = consumer.Consumer(session_data, self.store)
    
    def get_realm(self):
        if self.is_https():
            return 'https://%s/' % Site.objects.get_current().domain
        return 'http://%s/' % Site.objects.get_current().domain
    
    def get_callback_url(self):
        return urlparse.urljoin(self.get_realm(),
            reverse('socialregistration:openid:callback'))
    
    def get_redirect_url(self):
        auth_request = self.consumer.begin(self.endpoint_url)
        
        if AX_URLS:
            ax_request = ax.FetchRequest()
            for value in AX_URLS:
                url, is_required = value
                ax_request.add(ax.AttrInfo(url, required=is_required))
            # update with new items
            auth_request.addExtension(ax_request)

        redirect_url = auth_request.redirectURL(self.get_realm(),
            self.get_callback_url())
        
        return redirect_url
    
    def complete(self, GET, path):
        self.result = self.consumer.complete(GET, urlparse.urljoin(self.get_realm(),
            path))
    
    def is_valid(self):
        return self.result.status == consumer.SUCCESS
    
    def get_identity(self):
        return self.result.identity_url
    
    @staticmethod
    def get_session_key():
        return '%sopenid' % SESSION_KEY
