from json import JSONEncoder
from urllib2 import urlparse
from django.contrib.sites.models import get_current_site
from django.core import paginator
from django.core.paginator import EmptyPage, InvalidPage
from django.core.serializers import serialize
from django.db.models.query import QuerySet
from django.forms import widgets
from django.http import HttpResponse, QueryDict
from django.template.loader import render_to_string
from django.utils.encoding import force_unicode
from django.utils.functional import Promise
from django.views.generic.base import TemplateView
from django.views.generic.list import ListView


class LazyEncoder(JSONEncoder):

    def default(self, obj):
        if isinstance(obj, Promise):
            return force_unicode(obj)
        return super(LazyEncoder, self).default(obj)


class JsonResponse(HttpResponse):

    def __init__(self, object):
        if isinstance(object, QuerySet):
            content = serialize('json', object)
        else:
            content = LazyEncoder().encode(object)
        super(JsonResponse, self).__init__(
            content, content_type='application/json')


class JsonMixin(object):

    http_method_names = ['get', 'post']
    json_method_postfix = 'ajax'

    def get_context_data_ajax(self, **kwargs):
        if isinstance(self, ListView):
            raise NotImplementedError('ajax context data not defined')
        else:
            return {}

    def get_ajax(self, request, *args, **kwargs):
        return JsonResponse(self.get_context_data_ajax(**kwargs))

    def dispatch(self, request, *args, **kwargs):
        request_method = request.method.lower()
        if request_method in self.http_method_names:
            json_method = '%(method)s_%(postfix)s'.lower() % {'method': request_method,
                                                              'postfix': self.json_method_postfix}
            if request.is_ajax():
                if hasattr(self, json_method):
                    handler = getattr(self, json_method)
                else:
                    raise NotImplementedError('%s is not implemented' % json_method)
            else:
                handler = getattr(self, request.method.lower(), self.http_method_not_allowed)
        else:
            handler = self.http_method_not_allowed
        self.request = request
        self.args = args
        self.kwargs = kwargs
        return handler(request, *args, **kwargs)


class Paginator(paginator.Paginator):

    def __init__(self, *args, **kwargs):
        request = kwargs.pop('request', None)
        super(Paginator, self).__init__(*args, **kwargs)
        if request:
            self.path = request.path
            request_params = QueryDict(request.META['QUERY_STRING'], mutable=True)
            request_params.pop('page', None)
            request_params.pop('_', None)
            self.link_postfix = request_params.urlencode()

    def page(self, number):
        try:
            page = super(Paginator, self).page(number)
        except (EmptyPage, InvalidPage):
            page = super(Paginator, self).page(self.num_pages)
        for attr in ('link_postfix', 'path'):
            if hasattr(self, attr):
                setattr(page, attr, getattr(self, attr))
        return page


class BaseTemplateView(TemplateView):

    def get_context_data(self, **kwargs):
        context = super(BaseTemplateView, self).get_context_data(**kwargs)
        current_site = get_current_site(self.request)
        context['site_name'] = current_site.name
        return context


class BaseListView(JsonMixin, ListView):

    paginator_class = Paginator
    paginate_by = 5

    def search(self, queryset, text):
        return queryset

    def filter(self, queryset):
        return queryset

    def get_queryset(self):
        queryset = super(BaseListView, self).get_queryset()

        queryset = self.filter(queryset)
        self.search_text = self.request.GET.get('q')
        if self.search_text:
            queryset = self.search(queryset, self.search_text.upper())
        return queryset

    def get_paginator(self, queryset, per_page, orphans=0, allow_empty_first_page=True):
        """
        Return an instance of the paginator for this view.
        """
        return self.paginator_class(queryset, per_page, orphans=orphans,
                                    allow_empty_first_page=allow_empty_first_page, request=self.request)

    def get_ajax(self, request, *args, **kwargs):
        self.object_list = self.get_queryset()
        return JsonResponse(self.get_context_data_ajax(object_list=self.object_list))

    def get_context_data(self, **kwargs):
        context = super(BaseListView, self).get_context_data(**kwargs)
        context['search'] = self.search_text
        return context

    def get_context_data_ajax(self, **kwargs):
        context = self.get_context_data(**kwargs)
        return {'template': render_to_string(self.template_name_ajax, context)}


def get_referer_url(request, default=None):
    """
    Return the referer url of the current request

    """

    # if the user typed the url directly in the browser's address bar
    referer = request.META.get('HTTP_REFERER')
    if not referer:
        return default

    referer = urlparse.urlparse(referer)
    request_url = urlparse.urlparse(request.build_absolute_uri())
    if referer.hostname != request_url.hostname:
        return default

    return referer.path + ('?' + referer.query if referer.query else '')


class CheckBox(widgets.CheckboxInput):
    input_type = 'checkbox'
