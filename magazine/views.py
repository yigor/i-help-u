from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.db.models.query_utils import Q
from django.shortcuts import get_object_or_404, redirect
from django.utils.decorators import method_decorator
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView
from ihelpu.utils import BaseListView, get_referer_url
from magazine.forms import CommentForm
from magazine.models import Article, Comment
from vacancy.models import Vacancy


class MagazineView(BaseListView):

    model = Article
    template_name = 'article/list.html'
    template_name_ajax = 'article/list_table.html'
    paginate_by = 6

    def get_queryset(self):
        queryset = super(MagazineView, self).get_queryset().filter(is_active=True)
        queryset = queryset.order_by('-is_main', '-date_time')
        return queryset

    def search(self, queryset, text):
        return queryset.filter(Q(title__icontains=text) |
                               Q(body__icontains=text))


class ArticleView(DetailView):

    model = Article
    template_name = 'article/detail.html'

    def get_context_data(self, **kwargs):
        context = super(ArticleView, self).get_context_data(**kwargs)
        recommended_vacancies_queryset = self.object.recommended_vacancies.all()
        if not recommended_vacancies_queryset.exists():
            recommended_vacancies_queryset = Vacancy.objects.filter(topics__in=self.object.topics.all())

        context.update({'go_back_url': get_referer_url(self.request, reverse('magazine')),
                        'recommended_vacancies': recommended_vacancies_queryset[:3],
                        'more_recommended_vacancies': recommended_vacancies_queryset.count() > 3,
                        'comments': self.object.comments.filter(parent__isnull=True)})
        return context


class CommentCreateView(CreateView):

    model = Comment
    form_class = CommentForm

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(CommentCreateView, self).dispatch(request, *args, **kwargs)

    def get(self, *args, **kwargs):
        self.article = get_object_or_404(Article, id=kwargs['article_id'])
        return redirect(self.get_success_url())

    def get_form_kwargs(self):
        self.article = get_object_or_404(Article, id=self.kwargs['article_id'])
        parent_id = self.request.REQUEST.get('parent')
        parent_comment = get_object_or_404(Comment, id=parent_id) if parent_id else None

        kwargs = super(CommentCreateView, self).get_form_kwargs()
        kwargs.update({'author': self.request.user, 'article': self.article, 'parent': parent_comment})
        return kwargs

    def get_success_url(self):
        return reverse('article', kwargs={'pk': self.article.id})
