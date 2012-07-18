from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseRedirect

from django.contrib.auth import logout
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User

from socialregistration.contrib.facebook_js.client import Facebook
from socialregistration.contrib.facebook_js.models import FacebookProfile
from socialregistration.views import OAuthRedirect, OAuthCallback, Setup, SetupCallback


class FacebookCallback(OAuthCallback):
    client = Facebook
    profile = FacebookProfile
    template_name = 'socialregistration/facebook_js/facebook.html'

    def generate_username(self, request):
        return 'fb-%s' %(request.POST.get('username'))

    def update_or_create_user(self, request, user):
        """
        :param request: The current request object
        :param user: The unsaved user object
        """
        username = self.generate_username(request)

        user, is_new = User.objects.get_or_create(username=username)

        user.username = username
        user.email = request.POST.get('email')
        user.first_name = request.POST.get('first_name')
        user.last_name = request.POST.get('last_name')
        user.set_unusable_password()
        user.save()

        return user, is_new

    def post(self, request, *args, **kwargs):
        """
        Perform the combined GET and POST functions that normally take place
        """
        client = self.get_client()()
        request.session[self.get_client().get_session_key()] = client
        try:
            client = request.session[self.get_client().get_session_key()]
        except KeyError:
            return self.render_to_response({'error': "Session expired."})

        if request.POST.get('accessToken') is not None:
            client.access_token = request.POST.get('accessToken')
        # Get the lookup dictionary to find the user's profile
        lookup_kwargs = self.get_lookup_kwargs(request, client)

        # Logged out user - let's see if we've got the identity saved already.
        # If so - just log the user in. If not, create profile and redirect
        # to the setup view 
        user = request.user
        user, is_new = self.update_or_create_user(request, user)
        # Get profile
        profile, profile_is_new = self.get_model().objects.get_or_create(user=user, **lookup_kwargs)

        if profile_is_new:
            profile.user = user
            profile.save()
            if hasattr(client, 'access_token'):
                self.send_connect_signal(request, user, profile, client)
            self.delete_session_data(request) # @TODO remove?

        user = profile.authenticate()

        # No user existing - create a new one and redirect to the final setup view
        self.store_user(request, user)
        self.store_profile(request, profile)
        self.store_client(request, client)

        # Inactive user - displaying / redirect to the appropriate place.
        # if not user.is_active:
        #     return self.inactive_response()

        # Active user with existing profile: login, send signal and redirect
        self.login(request, user)
        self.send_login_signal(request, user, profile, client)

        return HttpResponse()

    def get_lookup_kwargs(self, request, client):
        return {'uid': request.POST.get('id')}

    def get_redirect(self):
        return reverse('socialregistration:facebook:setup')

class FacebookSetup(Setup, SetupCallback):
    client = Facebook
    profile = FacebookProfile
    template_name = 'socialregistration/facebook_js/facebook.html'

    def get_lookup_kwargs(self, request, client):
        return {'uid': client.get_user_info()['id']}
