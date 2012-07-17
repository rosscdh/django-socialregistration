from django.conf import settings

FACEBOOK_API_KEY = getattr(settings, 'FACEBOOK_API_KEY', None)
FACEBOOK_SECRET_KEY = getattr(settings, 'FACEBOOK_SECRET_KEY', None)
FACEBOOK_REQUEST_PERMISSIONS = getattr(settings, 'FACEBOOK_REQUEST_PERMISSIONS', None)

def FacebookTemplateVars(request):
    """
    Provides the facebook variables
    FACEBOOK_API_KEY
    FACEBOOK_SECRET_KEY
    FACEBOOK_REQUEST_PERMISSIONS
    """
    return {
    'FACEBOOK_API_KEY': FACEBOOK_API_KEY,
    'FACEBOOK_SECRET_KEY': FACEBOOK_SECRET_KEY,
    'FACEBOOK_REQUEST_PERMISSIONS': FACEBOOK_REQUEST_PERMISSIONS,
    }
