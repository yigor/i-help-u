# coding=utf-8
from django.conf import settings
from django.core.urlresolvers import reverse
from django.core.validators import RegexValidator
from django.db import models
from ihelpu.models import Topic


class Article(models.Model):

    class Meta:
        verbose_name = u'статья'
        verbose_name_plural = u'статьи'
        ordering = ('date_time', )

    def __unicode__(self):
        return self.title

    title = models.CharField(verbose_name=u'название', max_length=128)
    summary = models.CharField(verbose_name=u'сводка', max_length=256, blank=True)
    body = models.TextField(verbose_name=u'текст')
    cover_photo = models.ImageField(verbose_name=u'фотография обложки', upload_to='articles/%Y/%m/%d', blank=True)
    home_photo = models.ImageField(verbose_name=u'фотография на главной', upload_to='articles/%Y/%m/%d', blank=True)
    cover_background = models.CharField(verbose_name=u'фон обложки', max_length=8, blank=True, default='#FFFFFF',
                                        validators=[RegexValidator('^#[a-zA-Z0-9]{3,6}$')])
    is_main = models.BooleanField(verbose_name=u'главная', blank=True, default=False)
    topics = models.ManyToManyField(Topic, verbose_name=u'темы', blank=True)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=u'автор', related_name='articles',
                               null=True, blank=True)
    author_name = models.CharField(verbose_name=u'имя автора', max_length=128, blank=True)
    photographer = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=u'фотограф', related_name='photosets',
                                     null=True, blank=True)
    photographer_name = models.CharField(verbose_name=u'имя фотографа', max_length=128, blank=True)
    date_time = models.DateTimeField(verbose_name=u'дата', auto_now_add=True)
    recommended_vacancies = models.ManyToManyField('vacancy.Vacancy', blank=True)
    is_active = models.BooleanField(verbose_name=u'активная', blank=True, default=True)

    def get_absolute_url(self):
        return reverse('article', args=[str(self.id)])


class Comment(models.Model):

    article = models.ForeignKey(Article, verbose_name=u'статья', related_name='comments')
    parent = models.ForeignKey('self', related_name='children', blank=True, null=True)
    body = models.TextField(verbose_name=u'текст')
    author = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=u'автор', null=True, blank=True)
    date_time = models.DateTimeField(verbose_name=u'дата', auto_now_add=True)
