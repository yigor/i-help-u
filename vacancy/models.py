# coding=utf-8
from django.conf import settings
from django.core.urlresolvers import reverse
from django.core.validators import RegexValidator
from django.db import models
from ihelpu.models import Topic
from magazine.models import Article


class Organization(models.Model):

    class Meta:
        verbose_name = u'организация'
        verbose_name_plural = u'организации'
        ordering = ('-id', )

    def __unicode__(self):
        return self.title

    title = models.CharField(verbose_name=u'название', max_length=256)
    slogan = models.CharField(verbose_name=u'слоган', max_length=384, blank=True)
    description = models.TextField(verbose_name=u'описание')
    topics = models.ManyToManyField(Topic, verbose_name=u'темы', blank=True)
    logo = models.ImageField(verbose_name=u'логотип', upload_to='organizations/%Y/%m/%d', blank=True)
    cover_photo = models.ImageField(verbose_name=u'фотография обложки', upload_to='organizations/%Y/%m/%d', blank=True)
    cover_background = models.CharField(verbose_name=u'фон обложки', max_length=8, blank=True, default='#FFFFFF',
                                        validators=[RegexValidator('^#[a-zA-Z0-9]{3,6}$')])
    city = models.CharField(verbose_name=u'город', max_length=32)
    zip_code = models.CharField(verbose_name=u'почтовый индекс', max_length=6, blank=True)
    address_line = models.CharField(verbose_name=u'адрес', max_length=128, blank=True)
    contact_person = models.CharField(verbose_name=u'контактное лицо', max_length=128, blank=True)
    email = models.EmailField(verbose_name=u'email')
    phone_number = models.CharField(verbose_name=u'телефон', max_length=18, blank=True)
    web_site = models.URLField(verbose_name=u'сайт', blank=True)

    def get_absolute_url(self):
        return reverse('organization_detail', args=[str(self.id)])


class SocialLink(models.Model):

    class Meta:
        verbose_name = u'адрес в социальной сети'
        verbose_name_plural = u'адресы в социальной сети'
        unique_together = ('network', 'identity')

    def __unicode__(self):
        return self.identity

    SOCIAL_NETWORKS = (
        ('vkontakte', u'вконтакте'),
        ('facebook', u'facebook'),
        ('twitter', u'twitter'),
    )

    network = models.CharField(u'сеть',
                               db_index=True,
                               max_length=255,
                               choices=SOCIAL_NETWORKS)
    identity = models.URLField(u'адрес',
                               max_length=255)
    organization = models.ForeignKey(Organization, verbose_name=u'организация', related_name='social_links')


class Vacancy(models.Model):

    class Meta:
        verbose_name = u'вакансия'
        verbose_name_plural = u'вакансии'
        ordering = ('-id', )

    def __unicode__(self):
        return self.title

    organization = models.ForeignKey(Organization, verbose_name=u'организация', related_name='vacancies')
    title = models.CharField(verbose_name=u'название', max_length=128)
    description = models.TextField(verbose_name=u'описание')
    cover_photo = models.ImageField(verbose_name=u'фотография обложки', upload_to='vacancies/%Y/%m/%d', blank=True)
    cover_background = models.CharField(verbose_name=u'фон обложки', max_length=8, blank=True, default='#FFFFFF',
                                        validators=[RegexValidator('^#[a-zA-Z0-9]{3,6}$')])
    topics = models.ManyToManyField(Topic, verbose_name=u'темы')
    is_continuous = models.BooleanField(verbose_name=u'постоянная')
    responses = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='vacancies', through='VacancyRespond')
    recommended_vacancies = models.ManyToManyField('self', blank=True)

    def get_absolute_url(self):
        return reverse('vacancy_detail', args=[str(self.id)])

    @property
    def recommended_articles(self):
        return Article.objects.filter(topics__in=self.topics.all())


class VacancyRespond(models.Model):

    class Meta:
        verbose_name = u'отзыв на вакансии'
        verbose_name_plural = u'отзывы на вакансии'
        ordering = ('-response_date', )

    vacancy = models.ForeignKey(Vacancy, verbose_name=u'вакансия')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=u'пользователь')
    response_date = models.DateTimeField(verbose_name=u'дата отклика', auto_now_add=True, null=True)
    user_contacted = models.BooleanField(verbose_name=u'с пользователем связались', default=False)
    contact_date = models.DateTimeField(verbose_name=u'дата контакта', blank=True, null=True)
    user_hired = models.BooleanField(verbose_name=u'пользователь нанят', default=False)
