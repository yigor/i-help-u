import itertools
from django.db.models.query_utils import Q
from django.views.generic.base import TemplateView
from account.models import User
from ihelpu.utils import BaseListView
from magazine.models import Article
from vacancy.models import Vacancy, Organization


class HomeView(BaseListView):

    template_name = 'home.html'
    model = Article
    paginate_by = 9

    def get_queryset(self):
        queryset = super(HomeView, self).get_queryset()
        queryset = queryset.filter(is_active=True, is_main=False).order_by('-date_time')
        return queryset

    def get_context_data(self, **kwargs):
        context = super(HomeView, self).get_context_data(**kwargs)
        try:
            context['main_article'] = self.model.objects.filter(is_main=True)[0]
        except IndexError:
            pass
        context['first_column'] = context['object_list'][0::3]
        context['second_column'] = context['object_list'][1::3]
        context['third_column'] = context['object_list'][2::3]
        return context


class TeamView(TemplateView):
    template_name = 'team.html'


class AboutView(TemplateView):
    template_name = 'about.html'


class SearchView(BaseListView):

    template_name = 'search.html'
    template_name_ajax = 'search_table.html'

    def get_queryset(self):
        self.section = self.request.GET.get('section')
        self.search_text = self.request.GET.get('q', '')
        # remove odd spaces
        search_text = ' '.join([w.strip() for w in self.search_text.split(' ') if w]).upper()
        if not self.search_text and not self.section:
            return list()
        querysets = []
        if not self.section or self.section == 'article':
            q = (Q(title__icontains=search_text)
                 | Q(summary__icontains=search_text)) if search_text else Q()
            querysets.append(Article.objects.filter(q).extra(select={'type': 1}).values_list(
                'id', 'title', 'summary', 'type'))
        if not self.section or self.section == 'vacancy':
            q = (Q(title__icontains=search_text)
                 | Q(description__icontains=search_text)) if search_text else Q()
            querysets.append(Vacancy.objects.filter(q).extra(select={'type': 2}).values_list(
                'id', 'title', 'description', 'type'))
        if not self.section or self.section == 'org':
            q = (Q(title__icontains=search_text)
                 | Q(description__icontains=search_text)) if search_text else Q()
            querysets.append(Organization.objects.filter(q).extra(select={'type': 3}).values_list(
                'id', 'title', 'description', 'type'))
        if not self.section or self.section == 'user':
            query_param = '%' + search_text + '%'
            querysets.append(User.objects.filter(is_superuser=False, is_active=True).extra(
                select={'type': 4},
                where=["upper(concat(first_name, ' ', last_name)) like %s "
                       "or upper(concat(last_name, ' ', first_name)) like %s"],
                params=[query_param, query_param]).values_list('id', 'first_name', 'last_name', 'type'))
        return list(itertools.chain(*querysets))

    def get_context_data(self, **kwargs):
        context = super(SearchView, self).get_context_data(**kwargs)
        context['section'] = self.section
        return context
