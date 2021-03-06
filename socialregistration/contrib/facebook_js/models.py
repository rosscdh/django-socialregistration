from django.conf import settings
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.db import models
from socialregistration.signals import connect, login

class FacebookProfile(models.Model):
    user = models.ForeignKey(User, unique=True)
    site = models.ForeignKey(Site, default=Site.objects.get_current)
    uid = models.CharField(max_length=255, blank=False, null=False)

    class Meta:
        db_table = 'socialregistration_facebookprofile'

    def __unicode__(self):
        try:
            return u'%s: %s' % (self.user, self.uid)
        except User.DoesNotExist:
            return u'None'

    def authenticate(self):
        return authenticate(uid=self.uid)

class FacebookAccessToken(models.Model):
    profile = models.OneToOneField(FacebookProfile, related_name='access_token')
    access_token = models.CharField(max_length=255)

    class Meta:
        db_table = 'socialregistration_facebookaccesstoken'

def save_facebook_token(sender, user, profile, client, **kwargs):
    if hasattr(client, 'access_token'):
        try:
            FacebookAccessToken.objects.get(profile=profile).delete()
        except FacebookAccessToken.DoesNotExist:
            pass

        FacebookAccessToken.objects.create(profile=profile,
            access_token=client.access_token)

connect.connect(save_facebook_token, sender=FacebookProfile,
    dispatch_uid='socialregistration.facebook.connect')
login.connect(save_facebook_token, sender = FacebookProfile,
    dispatch_uid = 'socialregistration.facebook.login')