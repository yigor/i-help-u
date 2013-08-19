# coding=utf-8
import random
import string
import urlparse
from datetime import timedelta
from django.conf import settings
from django.contrib.auth import login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordResetForm, PasswordChangeForm, SetPasswordForm
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.models import get_current_site
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, Http404
from django.shortcuts import get_object_or_404, redirect, resolve_url
from django.template.context import RequestContext
from django.template.loader import render_to_string
from django.template.response import TemplateResponse
from django.utils.decorators import method_decorator
from django.utils.http import base36_to_int, int_to_base36, is_safe_url
from django.utils.timezone import now
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.debug import sensitive_post_parameters
from django.views.generic.detail import DetailView
from django.views.generic.edit import UpdateView, FormView
from account.forms import UserProfileForm, UserPhotoForm, RegistrationForm, LoginForm
from account.models import User
from ihelpu.utils import JsonResponse, get_referer_url, BaseTemplateView
from vacancy.models import Vacancy


class RegistrationView(FormView):

    template_name = 'account/registration/registration_form.html'
    form_class = RegistrationForm

    def get_template_names(self):
        if self.request.is_ajax():
            return [self.template_name]
        return ['account/registration/registration_container.html']

    def get_context_data(self, **kwargs):
        context = super(RegistrationView, self).get_context_data(**kwargs)
        context['rand'] = ''.join(random.choice(string.ascii_lowercase) for x in range(5))
        return context

    def form_valid(self, form):

        user = User.objects.create_user(form.cleaned_data['email'],
                                        form.cleaned_data['email'],
                                        form.cleaned_data['password1'])
        user.first_name = form.cleaned_data['first_name']
        user.last_name = form.cleaned_data['last_name']
        user.is_active = False
        user.save()

        user.assign_activation_key()

        confirm_link = self.request.build_absolute_uri(reverse('account:email_confirm_done',
                                                               kwargs={'token': user.activation_key,
                                                                       'uidb36': int_to_base36(user.id)}))
        current_site = get_current_site(self.request)
        site_name = current_site.name
        context = {'site_name': site_name, 'link': confirm_link}

        subject = render_to_string('mail/email_confirm_subject.txt', context)
        body = render_to_string('mail/email_confirm_body.html', context)

        user.email_user(''.join(subject.splitlines()), body)
        return JsonResponse({'status': True, 'redirect': reverse('account:email_confirm')})

    def form_invalid(self, form):
        return JsonResponse({'status': False,
                             'template': render_to_string(self.template_name,
                                                          self.get_context_data(form=form),
                                                          context_instance=RequestContext(self.request))})


class SocialRegistrationComplete(BaseTemplateView):

    template_name = 'account/registration/social_registration_complete.html'


class EmailConfirmationView(BaseTemplateView):

    template_name = 'account/registration/email_confirmation.html'

    def get(self, request, *args, **kwargs):
        activation_key = self.kwargs.get('token')
        uidb36 = self.kwargs.get('uidb36')
        if not activation_key or not uidb36:
            return super(EmailConfirmationView, self).get(request, *args, **kwargs)
        user = get_object_or_404(User, pk=base36_to_int(uidb36), is_active=False)
        if user.activation_key == activation_key \
                and user.date_joined > (now() - timedelta(days=1)):
            user.is_active = True
            user.save()
            user.backend = 'django.contrib.auth.backends.ModelBackend'
            auth_login(request, user)
            user.activation_key = ''
            user.save()
            return redirect('account:profile_edit')
        raise Http404()


class UserProfileUpdateView(UpdateView):

    model = User
    form_class = UserProfileForm
    template_name = 'account/profile/user_form.html'

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(UserProfileUpdateView, self).dispatch(request, *args, **kwargs)

    def get_object(self, queryset=None):
        return self.request.user

    def get_context_data(self, **kwargs):
        context = super(UserProfileUpdateView, self).get_context_data(**kwargs)
        request_url = urlparse.urlparse(self.request.build_absolute_uri())
        context['domain'] = request_url.netloc
        if self.request.method == 'GET':
            context['action'] = self.request.GET.get('action', '')
        return context

    def form_valid(self, form):
        self.object = form.save()
        if not self.object.is_active:
            self.object.is_active = True
            self.object.save()
        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        success_url = self.request.GET.get('next')
        return success_url or reverse('account:profile_own_show')


class ChangePhotoView(UpdateView):

    model = User
    form_class = UserPhotoForm
    template_name = 'account/profile/photo_change_form.html'

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        if request.method == 'GET' and not request.is_ajax():
            return redirect(reverse('account:profile_edit') + '?action=photo')
        return super(ChangePhotoView, self).dispatch(request, *args, **kwargs)

    def get_object(self, queryset=None):
        return self.request.user

    def form_valid(self, form):
        self.object = form.save()
        return redirect(reverse('account:profile_edit'))

    def form_invalid(self, form):
        #todo: show error
        return redirect(reverse('account:profile_edit'))


class UserProfileDetailView(DetailView):

    model = User
    template_name = 'account/profile/user_detail.html'

    def get_object(self, queryset=None):
        if not self.kwargs:
            return self.request.user
        return super(UserProfileDetailView, self).get_object(queryset)

    def dispatch(self, *args, **kwargs):
        return super(UserProfileDetailView, self).dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(UserProfileDetailView, self).get_context_data(**kwargs)

        responded_vacancies_queryset = self.object.vacancies.all()
        recommended_vacancies_queryset = Vacancy.objects.filter(topics__in=self.object.interests.all())

        context.update({'go_back_url': get_referer_url(self.request, reverse('home')),
                        'responded_vacancies': responded_vacancies_queryset[:3],
                        'more_responded_vacancies': responded_vacancies_queryset.count() > 3,
                        'recommended_vacancies': recommended_vacancies_queryset[:3],
                        'more_recommended_vacancies': recommended_vacancies_queryset.count() > 3})
        return context


def logout(request):
    auth_logout(request)
    return redirect('home')


@sensitive_post_parameters()
@csrf_protect
@never_cache
def login(request):
    """
    Displays the login form and handles the login action.
    """
    redirect_to = request.REQUEST.get('next', '')
    if not redirect_to:
        redirect_to = get_referer_url(request)

    if request.method == "POST":
        form = LoginForm(data=request.POST)
        if form.is_valid():

            # Ensure the user-originating redirection url is safe.
            if not is_safe_url(url=redirect_to, host=request.get_host()):
                redirect_to = resolve_url(settings.LOGIN_REDIRECT_URL)

            if not form.cleaned_data.get('remember_me'):
                request.session.set_expiry(0)

            # Okay, security check complete. Log the user in.
            auth_login(request, form.get_user())

            if request.session.test_cookie_worked():
                request.session.delete_test_cookie()

            return  JsonResponse({'status': True, 'redirect': redirect_to})
        else:
            status = False
    else:
        form = LoginForm(request)
        status = True

    request.session.set_test_cookie()

    request_url = urlparse.urlparse(request.build_absolute_uri())

    context = {
        'form': form,
        'next': redirect_to or '',
        'domain': request_url.netloc,
        'rand': ''.join(random.choice(string.ascii_lowercase) for x in range(5))
    }

    if request.is_ajax():
        return JsonResponse({'status': status, 'template': render_to_string(
            'account/login/login_form.html', context, context_instance=RequestContext(request))})
    return TemplateResponse(request, 'account/login/login_container.html', context)


@csrf_protect
def password_reset(request):
    post_reset_redirect = reverse('django.contrib.auth.views.password_reset_done')
    if request.method == "POST":
        form = PasswordResetForm(request.POST)
        if form.is_valid():
            opts = {
                'use_https': request.is_secure(),
                'token_generator': default_token_generator,
                'from_email': None,
                'email_template_name': 'mail/password_reset_body.html',
                'subject_template_name': 'mail/password_reset_subject.txt',
                'request': request,
            }
            form.save(**opts)
            return JsonResponse({'status': True, 'redirect': post_reset_redirect})
        else:
            status = False
    else:
        form = PasswordResetForm()
        status = True
    context = {
        'form': form,
    }
    if request.is_ajax():
        return JsonResponse({'status': status, 'template': render_to_string(
            'account/password_reset/reset_form.html', context, context_instance=RequestContext(request))})
    return TemplateResponse(request, 'account/password_reset/reset_container.html', context)


@sensitive_post_parameters()
@never_cache
def password_reset_confirm(request, uidb36=None, token=None):
    """
    View that checks the hash in a password reset link and presents a
    form for entering a new password.
    """
    assert uidb36 is not None and token is not None  # checked by URLconf
    post_reset_redirect = reverse('django.contrib.auth.views.password_reset_complete')
    try:
        uid_int = base36_to_int(uidb36)
        user = User.objects.get(pk=uid_int)
    except (ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        validlink = True
        if request.method == 'POST':
            form = SetPasswordForm(user, request.POST)
            if form.is_valid():
                form.save()
                return JsonResponse({'status': True, 'redirect': post_reset_redirect})
            else:
                status = False
        else:
            form = SetPasswordForm(None)
            status = True
    else:
        raise Http404
    context = {'form': form, 'validlink': validlink, 'uidb36': uidb36, 'token': token}
    if request.is_ajax():
        return JsonResponse({'status': status, 'template': render_to_string(
            'account/password_reset/confirm_form.html', context, context_instance=RequestContext(request))})
    return TemplateResponse(request, 'account/password_reset/confirm_container.html', context)


@sensitive_post_parameters()
@csrf_protect
@login_required
def password_change(request):
    if not request.is_ajax():
        return redirect(reverse('account:profile_edit') + '?action=password')

    template_name = 'account/profile/password_change_form.html'
    post_change_redirect = reverse('account:profile_edit')
    if request.method == "POST":
        form = PasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            form.save()
            return JsonResponse({'status': True, 'redirect': post_change_redirect})
        else:
            status = False
    else:
        form = PasswordChangeForm(user=request.user)
        status = True
    context = {'form': form}
    if request.is_ajax():
        return JsonResponse({'status': status, 'template': render_to_string(
            template_name, context, context_instance=RequestContext(request))})
    return TemplateResponse(request, template_name, context)
