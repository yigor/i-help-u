# coding=utf-8
import hashlib
import os
import random
import urllib2
from datetime import datetime
from django.contrib.auth.models import AbstractUser
from django.core.files.base import File
from django.core.files.temp import NamedTemporaryFile
from django.db import models
from django.utils.functional import cached_property
from django_ulogin.models import ULoginUser
from django_ulogin.signals import assign
from imagekit.models import ImageSpecField
from imagekit.processors import SmartResize, ResizeToFit
from ihelpu.models import Topic
from magazine.models import Article
from vacancy.models import Vacancy


class AvatarProcessor(object):

    def process(self, img):
        if img.size[0] < 250 or img.size[1] < 250:
            actual_processor = ResizeToFit(250, 250)
        else:
            actual_processor = SmartResize(250, 250)
        return actual_processor.process(img)


class User(AbstractUser):

    def __unicode__(self):
        return '%s %s' % (self.first_name, self.last_name)

    GENDER_FEMALE = 1
    GENDER_MALE = 2
    GENDER_CHOICES = (
        (GENDER_MALE, u'Мужской'),
        (GENDER_FEMALE, u'Женский'),
    )

    gender = models.IntegerField(choices=GENDER_CHOICES, verbose_name=u'пол', null=True)
    photo = models.ImageField(null=True, blank=True, upload_to='photos/%Y/%m/%d', verbose_name=u'фото')
    avatar = ImageSpecField(image_field='photo',
                            processors=[AvatarProcessor()],
                            format='JPEG',
                            options={'quality': 90})
    avatar_small = ImageSpecField(image_field='photo',
                                  processors=[SmartResize(32, 32)],
                                  format='JPEG',
                                  options={'quality': 90})
    activation_key = models.CharField(blank=True, default='', max_length=40)
    city = models.CharField(default='', max_length=255, verbose_name=u'город')
    phone_number = models.CharField(blank=True, default='', max_length=18, verbose_name=u'телефон')
    hide_contacts = models.BooleanField(default=True, verbose_name=u'скрывать контакты в профиле')
    birth_date = models.DateField(blank=True, null=True, verbose_name=u'дата рождения',
                                  help_text=u'формат: "ДД.ММ.ГГГГ"')
    about = models.TextField(blank=True, default='', verbose_name=u'о себе')
    i_can = models.TextField(blank=True, default='', verbose_name=u'я могу')
    i_want = models.TextField(blank=True, default='', verbose_name=u'я хочу')
    web_site = models.URLField(verbose_name=u'сайт', blank=True)
    interests = models.ManyToManyField(Topic, blank=True, verbose_name=u'интересы')

    def assign_activation_key(self):
        salt = hashlib.sha1(str(random.random())).hexdigest()[:5]
        username = self.username.encode('utf-8')
        self.activation_key = hashlib.sha1(salt + username).hexdigest()
        self.save()

    @property
    def recommended_vacancies(self):
        return Vacancy.objects.filter(topics__in=self.interests.all())

    @property
    def recommended_articles(self):
        return Article.objects.filter(topics__in=self.interests.all())

    @cached_property
    def empty_social_profiles(self):
        filled_profiles = self.ulogin_users.values_list('network', flat=True)
        return ','.join({'vkontakte', 'facebook'} - set(filled_profiles))


def catch_ulogin_signal(*args, **kwargs):
    user = kwargs['user']
    json = kwargs['ulogin_data']

    if kwargs['registered']:
        #
        user.first_name = json['first_name']
        user.last_name = json['last_name']
        user.username = json['email']
        user.email = json['email']

        for field in ['city', 'gender']:
            if field in json:
                setattr(user, field, json.get(field))

        if 'bdate' in json and json['bdate']:
            d, m, y = json['bdate'].split('.')
            user.birth_date = datetime(int(y), int(m), int(d))

        photo_path = json.get('photo_big')
        if photo_path:
            img_temp = NamedTemporaryFile(delete=True)
            img_temp.write(urllib2.urlopen(photo_path).read())
            img_temp.flush()

            user.photo.save(os.path.basename(photo_path), File(img_temp))

        user.save()
    else:
        for field in ('first_name', 'last_name', 'city', 'gender'):
            if not getattr(user, field) and json.get(field):
                setattr(user, field, json.get(field))
        if not user.birth_date and 'bdate' in json and json['bdate']:
            d, m, y = json['bdate'].split('.')
            user.birth_date = datetime(int(y), int(m), int(d))
        user.save()


assign.connect(receiver=catch_ulogin_signal,
               sender=ULoginUser,
               dispatch_uid='accounts.models')
