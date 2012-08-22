from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseRedirect
from django.contrib.auth.models import User

from socialregistration.contrib.linkedin_js.client import LinkedIn
from socialregistration.contrib.linkedin_js.models import LinkedInProfile
from socialregistration.views import OAuthRedirect, OAuthCallback, SetupCallback


class LinkedInRedirect(OAuthRedirect):
    client = LinkedIn
    template_name = 'socialregistration/linkedin/linkedin.html'

class LinkedInCallback(OAuthCallback):
    client = LinkedIn
    profile = LinkedInProfile
    template_name = 'socialregistration/linkedin/linkedin.html'

    def generate_username(self, request):
        return 'in_%s' %(request.POST.get('id'))

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

        if request.POST.get('accessToken',None) is not None:
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
        self.send_profile_data_signal(request, user, request.POST, client)

        return HttpResponse()

    def get_lookup_kwargs(self, request, client):
        return {'linkedin_id': request.POST.get('id')}

    def get_redirect(self):
        return reverse('socialregistration:linkedin:setup')

class LinkedInSetup(SetupCallback):
    client = LinkedIn
    profile = LinkedInProfile
    template_name = 'socialregistration/linkedin/linkedin.html'
    
    def get_lookup_kwargs(self, request, client):
        return {'linkedin_id': client.get_user_info()['id']}
    
