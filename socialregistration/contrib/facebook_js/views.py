from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseRedirect

from django.contrib.auth import logout
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _

from socialregistration.contrib.facebook_js.client import Facebook
from socialregistration.contrib.facebook_js.models import FacebookProfile
from socialregistration.views import OAuthRedirect, OAuthCallback, Setup, SetupCallback


class FacebookCallback(OAuthCallback):
    client = Facebook
    template_name = 'socialregistration/facebook_js/facebook.html'

    def generate_username(self, request):
        return 'fb-%s' %(request.POST.get('id'))

    def generate_user(self, request, user, profile, client):
        """
        :param request: The current request object
        :param user: The unsaved user object
        :param profile: The unsaved profile object
        :param client: The API client
        """
        user.username = self.generate_username(request)
        user.set_unusable_password()
        user.save()

        profile.user = user
        profile.save()

        user = profile.authenticate()

        self.send_connect_signal(request, user, profile, client)

        self.login(request, user)

        self.send_login_signal(request, user, profile, client)

        self.delete_session_data(request)

        return user, profile, client

    def post(self, request, *args, **kwargs):
        """
        Perform the combined GET and POST functions that normally take place
        """
        try:
            client = request.session[self.get_client().get_session_key()]
        except KeyError:
            return self.render_to_response({'error': "Session expired."})

        # Get the lookup dictionary to find the user's profile
        lookup_kwargs = self.get_lookup_kwargs(request, client)

        # Logged out user - let's see if we've got the identity saved already.
        # If so - just log the user in. If not, create profile and redirect
        # to the setup view 
        user = self.authenticate(**lookup_kwargs)

        # No user existing - create a new one and redirect to the final setup view
        if user is None:
            user = self.create_user()
            profile = self.create_profile(user, **lookup_kwargs)

            self.store_user(request, user)
            self.store_profile(request, profile)
            self.store_client(request, client)

            # Generate the User dictionart
            self.generate_user(request, user, profile, client)

        # Inactive user - displaying / redirect to the appropriate place.
        if not user.is_active:
            return self.inactive_response()

        # Active user with existing profile: login, send signal and redirect
        self.login(request, user)

        profile = self.get_profile(user=user, **lookup_kwargs)

        self.send_login_signal(request, user, profile, client)

        return HttpResponse()

    def get_lookup_kwargs(self, request, client):
        print request.POST
        return {'uid': request.POST.get('id')}

    def get_redirect(self):
        return reverse('socialregistration:facebook:setup')

class FacebookSetup(Setup, SetupCallback):
    client = Facebook
    profile = FacebookProfile
    template_name = 'socialregistration/facebook_js/facebook.html'

    def get_lookup_kwargs(self, request, client):
        print request.POST
        return {'uid': client.get_user_info()['id']}
