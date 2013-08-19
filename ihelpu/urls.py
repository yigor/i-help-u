from django.conf.urls import patterns, url
from ihelpu.views import HomeView, AboutView, TeamView, SearchView

urlpatterns = patterns(
    '',
    url(r'^$', HomeView.as_view(), name='home'),
    url(r'^about/$', AboutView.as_view(), name='about'),
    url(r'^about/team/$', TeamView.as_view(), name='team'),
    url(r'^search/$', SearchView.as_view(), name='search'),
)
