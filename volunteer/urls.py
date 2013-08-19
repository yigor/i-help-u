from django.conf import settings
from django.conf.urls import patterns, include, url
from django.conf.urls.static import static
from django.contrib import admin
from ihelpu.sitemaps import sitemaps

admin.autodiscover()

urlpatterns = patterns(
    '',
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),

    url(r'^ulogin/', include('django_ulogin.urls')),

    url(r'^account/', include('account.urls', namespace='account')),

    url(r'^magazine/', include('magazine.urls')),
    url(r'^', include('ihelpu.urls')),
    url(r'^', include('vacancy.urls')),

    url(r'^account/password_reset/$', 'account.views.password_reset', name='password_reset'),
    url(r'^account/password_reset/done/$', 'django.contrib.auth.views.password_reset_done',
        kwargs={'template_name': 'account/password_reset/done.html'}),
    url(r'^account/password_reset/(?P<uidb36>[0-9A-Za-z]+)-(?P<token>.+)/$',
        'account.views.password_reset_confirm', name='password_reset_confirm'),
    url(r'^account/password_reset/complete/$', 'django.contrib.auth.views.password_reset_complete',
        kwargs={'template_name': 'account/password_reset/complete.html'}),

    # the sitemap
    (r'^sitemap\.xml$', 'django.contrib.sitemaps.views.sitemap', {'sitemaps': sitemaps})
)

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
