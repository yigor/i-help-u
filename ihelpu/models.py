# coding=utf-8
from django.db import models


class Topic(models.Model):

    class Meta:
        verbose_name = u'тема'
        verbose_name_plural = u'темы'
        ordering = ('id', )

    def __unicode__(self):
        return self.title

    title = models.CharField(verbose_name=u'название', max_length=128)
