from django.contrib.sitemaps import GenericSitemap
from magazine.models import Article
from vacancy.models import Organization, Vacancy

sitemaps = {
    'magazine': GenericSitemap({'queryset': Article.objects.filter(is_active=True),
                                'date_field': 'date_time'}, priority=0.9),
    'organization': GenericSitemap({'queryset': Organization.objects.all()}, priority=0.8),
    'vacancy': GenericSitemap({'queryset': Vacancy.objects.all()}, priority=0.7),
}
