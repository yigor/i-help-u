from django.conf.urls import patterns, url
from vacancy.views import OrganizationListView, OrganizationDetailView, \
    VacancyListView, VacancyDetailView, VacancyRespondView, VacancyRecommendedListView, VacancyRespondedView


urlpatterns = patterns(
    '',
    url(r'^organization/$', OrganizationListView.as_view(), name='organization_list'),
    url(r'^organization/(?P<pk>\d+)/$', OrganizationDetailView.as_view(), name='organization_detail'),
    url(r'^vacancy/$', VacancyListView.as_view(), name='vacancy_list'),
    url(r'^vacancy/recommended/(?P<subject_type>user|article|organization|vacancy)/(?P<subject_id>\d+)/$',
        VacancyRecommendedListView.as_view(), name='vacancy_recommended'),
    url(r'^vacancy/(?P<pk>\d+)/$', VacancyDetailView.as_view(), name='vacancy_detail'),
    url(r'^vacancy/(?P<pk>\d+)/respond/$', VacancyRespondView.as_view(), name='vacancy_respond'),
    url(r'^vacancy/responded/$', VacancyRespondedView.as_view(), name='vacancy_responded'),
)
