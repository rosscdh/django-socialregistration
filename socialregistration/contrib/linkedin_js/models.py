from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.db import models
from socialregistration.signals import connect, login

class LinkedInProfile(models.Model):
    user = models.ForeignKey(User, unique=True)
    site = models.ForeignKey(Site, default=Site.objects.get_current)
    linkedin_id = models.CharField(max_length=25)

    class Meta:
        app_label = 'socialregistration'
        db_table = 'socialregistration_linkedinprofile'

    def __unicode__(self):
        try:
            return u'%s: %s' % (self.user, self.linkedin_id)
        except User.DoesNotExist:
            return u'None'

    def authenticate(self):
        return authenticate(linkedin_id=self.linkedin_id)

class LinkedInRequestToken(models.Model):
    profile = models.OneToOneField(LinkedInProfile, related_name='request_token')
    oauth_token = models.CharField(max_length=80)
    oauth_token_secret = models.CharField(max_length=80)

    class Meta:
        app_label = 'socialregistration'
        db_table = 'socialregistration_linkedinrequesttoken'

class LinkedInAccessToken(models.Model):
    profile = models.OneToOneField(LinkedInProfile, related_name='access_token')
    oauth_token = models.CharField(max_length=80)
    oauth_token_secret = models.CharField(max_length=80)

    class Meta:
        app_label = 'socialregistration'
        db_table = 'socialregistration_linkedinaccesstoken'

def save_linkedin_token(sender, user, profile, client, **kwargs):
    try:
        LinkedInRequestToken.objects.get(profile=profile).delete()
    except LinkedInRequestToken.DoesNotExist:
        pass
    try:
        LinkedInAccessToken.objects.get(profile=profile).delete()
    except LinkedInAccessToken.DoesNotExist:
        pass
    
    LinkedInRequestToken.objects.create(profile=profile,
        oauth_token=client.get_request_token().key,
        oauth_token_secret=client.get_request_token().secret)
    
    LinkedInAccessToken.objects.create(profile=profile,
        oauth_token=client.get_access_token().key,
        oauth_token_secret=client.get_access_token().secret)


# Disconnect the signals for linkedin until we figure out how to get accessToken data from the js api
# connect.connect(save_linkedin_token, sender=LinkedInProfile,
#     dispatch_uid='socialregistration.linkedin.token')
# login.connect(save_linkedin_token, sender=LinkedInProfile,
#     dispatch_uid='socialregistration.linkedin.login')