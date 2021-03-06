from django.conf import settings

FACEBOOK_API_KEY = getattr(settings, 'FACEBOOK_API_KEY', None)
FACEBOOK_SECRET_KEY = getattr(settings, 'FACEBOOK_SECRET_KEY', None)
FACEBOOK_REQUEST_PERMISSIONS = getattr(settings, 'FACEBOOK_REQUEST_PERMISSIONS', None)
FACEBOOK_AUTO_LOGIN_IF_HAS_ACCOUNT = getattr(settings, 'FACEBOOK_AUTO_LOGIN_IF_HAS_ACCOUNT', False)

def FacebookTemplateVars(request):
    """
    Provides the facebook variables
    FACEBOOK_API_KEY
    FACEBOOK_SECRET_KEY
    FACEBOOK_REQUEST_PERMISSIONS
    FACEBOOK_AUTO_LOGIN_IF_HAS_ACCOUNT
    """
    return {
    'FACEBOOK_API_KEY': FACEBOOK_API_KEY,
    'FACEBOOK_SECRET_KEY': FACEBOOK_SECRET_KEY,
    'FACEBOOK_REQUEST_PERMISSIONS': FACEBOOK_REQUEST_PERMISSIONS,
    'FACEBOOK_AUTO_LOGIN_IF_HAS_ACCOUNT': FACEBOOK_AUTO_LOGIN_IF_HAS_ACCOUNT
    }
