from django.conf.urls import patterns, url
from account.views import UserProfileUpdateView, UserProfileDetailView, \
    RegistrationView, EmailConfirmationView, SocialRegistrationComplete, ChangePhotoView


urlpatterns = patterns(
    '',
    url(r'^register/$', RegistrationView.as_view(), name='register'),
    url(r'^register/complete/$', SocialRegistrationComplete.as_view(), name='register_social_complete'),
    url(r'^register/confirmation/$', EmailConfirmationView.as_view(),
        name='email_confirm'),
    url(r'^register/confirmation/(?P<uidb36>[0-9A-Za-z]+)-(?P<token>.+)/$', EmailConfirmationView.as_view(),
        name='email_confirm_done'),
    url(r'^profile/change_password/$', 'account.views.password_change', name='change_password'),
    url(r'^profile/change_photo/$', ChangePhotoView.as_view(), name='change_photo'),
    url(r'^profile/edit/$', UserProfileUpdateView.as_view(), name='profile_edit'),
    url(r'^profile/$', UserProfileDetailView.as_view(), name='profile_own_show'),
    url(r'^profile/(?P<pk>\d+)/$', UserProfileDetailView.as_view(), name='profile_show'),
    url(r'^login/$', 'account.views.login', name='login'),
    url(r'^logout/$', 'account.views.logout', name='logout'),
)
