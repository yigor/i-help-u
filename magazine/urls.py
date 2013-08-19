from django.conf.urls import patterns, url
from magazine.views import MagazineView, ArticleView, CommentCreateView

urlpatterns = patterns(
    '',
    url(r'^$', MagazineView.as_view(), name='magazine'),
    url(r'^(?P<pk>\d+)/$', ArticleView.as_view(), name='article'),
    url(r'^(?P<article_id>\d+)/comment/$', CommentCreateView.as_view(), name='comment_add'),
)
