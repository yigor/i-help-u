# coding=utf-8
from django.contrib.auth.decorators import login_required
from django.contrib.sites.models import get_current_site
from django.core.mail import send_mail
from django.core.urlresolvers import reverse
from django.db.models.query_utils import Q
from django.shortcuts import redirect, get_object_or_404
from django.template.loader import render_to_string
from django.utils.decorators import method_decorator
from django.views.generic.base import View
from django.views.generic.detail import DetailView, SingleObjectMixin
from account.models import User
from ihelpu.models import Topic
from ihelpu.utils import BaseListView, get_referer_url, BaseTemplateView
from magazine.models import Article
from vacancy.models import Organization, Vacancy, VacancyRespond


class OrganizationListView(BaseListView):

    model = Organization
    template_name = 'organization/list.html'
    template_name_ajax = 'organization/list_table.html'

    def search(self, queryset, text):
        return queryset.filter(Q(title__icontains=text) |
                               Q(description__icontains=text))

    def filter(self, queryset):
        try:
            self.topics = [int(t) for t in self.request.GET.getlist('topic', [])]
        except ValueError:
            self.topics = []
        if self.topics:
            queryset = queryset.filter(topics__in=self.topics)
        return queryset.distinct()

    def get_context_data(self, **kwargs):
        context = super(OrganizationListView, self).get_context_data(**kwargs)
        context.update({'topics': Topic.objects.all(), 'active_topics': self.topics})
        return context


class OrganizationDetailView(DetailView):

    model = Organization
    template_name = 'organization/detail.html'

    def get_context_data(self, **kwargs):
        context = super(OrganizationDetailView, self).get_context_data(**kwargs)

        own_vacancies_queryset = self.object.vacancies.all()
        recommended_vacancies_queryset = Vacancy.objects.filter(
            topics__in=self.object.topics.all()).exclude(organization=self.object)

        context.update({'go_back_url': get_referer_url(self.request, reverse('organization_list')),
                        'own_vacancies': own_vacancies_queryset[:9],
                        'more_own_vacancies': own_vacancies_queryset.count() > 9,
                        'recommended_vacancies': recommended_vacancies_queryset[:3],
                        'more_recommended_vacancies': recommended_vacancies_queryset.count() > 3})
        return context


class VacancyListView(BaseListView):

    model = Vacancy
    template_name = 'vacancy/list.html'
    template_name_ajax = 'vacancy/list_table.html'

    def filter(self, queryset):
        try:
            self.topics = [int(t) for t in self.request.GET.getlist('topic', [])]
        except ValueError:
            self.topics = []
        if self.topics:
            queryset = queryset.filter(topics__in=self.topics)
        self.continuous = self.request.GET['continuous'] if self.request.GET.get('continuous') in ['0', '1'] else None
        if self.continuous:
            queryset = queryset.filter(is_continuous=(self.continuous != '0'))
        self.recommended = self.request.GET.get('recommended', '0') == '1'
        if self.recommended:
            queryset = queryset.filter(topics__in=self.request.user.interests.all())
        return queryset.distinct()

    def search(self, queryset, text):
        return queryset.filter(Q(title__icontains=text) |
                               Q(description__icontains=text))

    def get_context_data(self, **kwargs):
        context = super(VacancyListView, self).get_context_data(**kwargs)
        context.update({'topics': Topic.objects.all(), 'active_topics': self.topics,
                        'continuous': self.continuous, 'recommended': self.recommended})
        return context


class VacancyRecommendedListView(BaseListView):

    model = Vacancy
    template_name_ajax = 'vacancy/recommended_list_table.html'
    paginate_by = 3

    def get_queryset(self):
        subject_type = self.kwargs['subject_type']
        subject_id = self.kwargs['subject_id']
        if subject_type == 'user':
            subject = get_object_or_404(User, pk=subject_id)
            return Vacancy.objects.filter(topics__in=subject.interests.all())
        elif subject_type == 'article':
            subject = get_object_or_404(Article, pk=subject_id)
            queryset = subject.recommended_vacancies.all()
            if not queryset.exists():
                queryset = Vacancy.objects.filter(topics__in=subject.topics.all())
            return queryset
        elif subject_type == 'organization':
            subject = get_object_or_404(Organization, pk=subject_id)
            return Vacancy.objects.filter(topics__in=subject.topics.all()).exclude(organization=subject.id)
        elif subject_type == 'vacancy':
            subject = get_object_or_404(Vacancy, pk=subject_id)
            queryset = subject.recommended_vacancies.all()
            if not queryset.exists():
                queryset = Vacancy.objects.filter(topics__in=subject.topics.all())
            return queryset.exclude(id=subject.id)

    def get_context_data(self, **kwargs):
        context = super(BaseListView, self).get_context_data(**kwargs)
        context.update(self.kwargs)
        return context


class VacancyDetailView(DetailView):

    model = Vacancy
    template_name = 'vacancy/detail.html'

    def get_context_data(self, **kwargs):
        context = super(VacancyDetailView, self).get_context_data(**kwargs)
        recommended_vacancies_queryset = self.object.recommended_vacancies.all()
        if not recommended_vacancies_queryset.exists():
            recommended_vacancies_queryset = Vacancy.objects.filter(topics__in=self.object.topics.all())
        recommended_vacancies_queryset = recommended_vacancies_queryset.exclude(id=self.object.id)
        context.update({'recommended_vacancies': recommended_vacancies_queryset[:3],
                        'more_recommended_vacancies': recommended_vacancies_queryset.count() > 3,
                        'go_back_url': get_referer_url(self.request, reverse('magazine'))})
        return context


class VacancyRespondView(SingleObjectMixin, View):

    model = Vacancy

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(VacancyRespondView, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        return self.respond(request)

    def post(self, request, *args, **kwargs):
        return self.respond(request)

    def respond(self, request):
        self.object = self.get_object()
        respond, created = VacancyRespond.objects.get_or_create(vacancy=self.object, user=request.user)

        if created:
            current_site = get_current_site(request)
            site_name = current_site.name
            domain = current_site.domain
            context = {'domain': domain, 'site_name': site_name,
                       'user': request.user, 'vacancy': self.object}
            subject = render_to_string('mail/vacancy_responded_subject.txt', context)
            body = render_to_string('mail/vacancy_responded_body.html', context)

            send_mail(''.join(subject.splitlines()), body, 'no-reply@i-help-u.ru',
                      [self.object.organization.email, 'volunteer@i-help-u.ru'], fail_silently=False)
        return redirect('vacancy_responded')


class VacancyRespondedView(BaseTemplateView):

    template_name = 'vacancy/responded.html'
