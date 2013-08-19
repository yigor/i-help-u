# coding: utf-8
from django.conf import settings
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.db.models.loading import get_model
from django.db.models.query_utils import Q
from django.http import HttpResponseBadRequest, QueryDict
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.shortcuts import redirect, render
from django.views.decorators.csrf import csrf_exempt
from django.views.generic.base import TemplateView
from django.views.generic.edit import FormView, DeleteView
from django.utils import simplejson
from django.utils.decorators import method_decorator
from django.views.generic.list import ListView
from django_ulogin import settings as s
from django_ulogin.models import ULoginUser
from django_ulogin.signals import assign
from django_ulogin.forms import PostBackForm
import requests
import uuid


class CsrfExemptMixin(object):
    """
    A mixin that provides a way to exempt view class out of CSRF validation
    """
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(CsrfExemptMixin, self).dispatch(request, *args, **kwargs)


class LoginRequiredMixin(object):
    """
    A mixin that provides a way to restrict anonymous access
    """
    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(LoginRequiredMixin, self).dispatch(request,
            *args, **kwargs)


class ULoginMixin(LoginRequiredMixin):
    """
    A mixin that provides a set of all identities for current
    authenticated user
    """
    def get_queryset(self):
        return ULoginUser.objects.filter(user=self.request.user)


class PostBackView(CsrfExemptMixin, FormView):
    """
    Accepts the post back data from ULOGIN service and authenticates the user
    """

    form_class = PostBackForm
    http_method_names = ['post']
    error_template_name = 'django_ulogin/error.html'

    def handle_authenticated_user(self, response):
        """
        Handles the ULogin response if user is already
        authenticated
        """
        ulogin = ULoginUser.objects.get_or_create(
            user=self.request.user,
            uid=response['uid'],
            network=response['network'],
            defaults={
                'identity': response['identity'],
            })[0]
        return self.request.user, ulogin, False

    def handle_anonymous_user(self, response):
        """
        Handles the ULogin response if user is not authenticated (anonymous)
        """
        try:
            ulogin = ULoginUser.objects.filter(Q(network=response['network'],
                                                 uid=response['uid']) |
                                               Q(user__email=response['email']))[0]
        except IndexError:
            User = get_model(*settings.AUTH_USER_MODEL.split('.'))
            user = User.objects.create(username=uuid.uuid4().hex[:30])
            registered = True
        else:
            user = ulogin.user
            registered = False

        ulogin = ULoginUser.objects.get_or_create(
            user=user,
            network=response['network'],
            identity=response['identity'],
            uid=response['uid'])[0]

        # Authenticate user
        if not hasattr(user, 'backend'):
            user.backend = s.AUTHENTICATION_BACKEND
        login(self.request, user)

        return user, ulogin, registered

    def form_valid(self, form):
        """
        The request from ulogin service is correct
        """
        response = self.ulogin_response(form.cleaned_data['token'],
                                        self.request.get_host())

        if 'error' in response:
            return render(self.request, self.error_template_name,
                    {'json': response})

        if self.request.user.is_authenticated():
            user, identity, registered = \
            self.handle_authenticated_user(response)
        else:
            user, identity, registered = \
            self.handle_anonymous_user(response)

        assign.send(sender=ULoginUser,
            user=self.request.user,
            request=self.request,
            registered=registered,
            ulogin_user=identity,
            ulogin_data=response)

        if registered or not user.is_active:
            query_dict = QueryDict('').copy()
            if self.request.GET.get(REDIRECT_FIELD_NAME):
                query_dict.update({REDIRECT_FIELD_NAME: self.request.GET[REDIRECT_FIELD_NAME]})
            return redirect('%s?%s' % (reverse(s.REGISTER_VIEW),
                                       query_dict.urlencode(safe='/')))
        return redirect(self.request.GET.get(REDIRECT_FIELD_NAME) or '/')

    def form_invalid(self, form):
        """
        Bad request from service
        """
        return HttpResponseBadRequest()

    def ulogin_response(self, token, host):
        """
        Makes a request to ULOGIN
        """
        return simplejson.loads(requests.get(s.TOKEN_URL, params={
            'token': token,
            'host': host
        }).content)


class CrossDomainView(TemplateView):
    """
    Document for avoid cross domain security policies
    """
    template_name = 'django_ulogin/ulogin_xd.html'


class IdentityListView(ULoginMixin, ListView):
    """
    The list of all social identities for current authenticated user
    """
    template_name = 'django_ulogin/identities.html'
    context_object_name = 'identities'


class IdentityDeleteView(ULoginMixin, DeleteView):
    """
    Deletes the given social identity from current authenticated user
    """
    template_name = 'django_ulogin/confirm_delete.html'
    context_object_name = 'identity'

    def get_success_url(self):
        return reverse('ulogin_identities_list')

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, {
            'instance': self.get_object()
        })
