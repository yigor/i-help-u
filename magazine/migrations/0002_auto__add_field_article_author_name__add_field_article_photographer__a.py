# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'Article.author_name'
        db.add_column(u'magazine_article', 'author_name',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=128, blank=True),
                      keep_default=False)

        # Adding field 'Article.photographer'
        db.add_column(u'magazine_article', 'photographer',
                      self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='photosets', null=True, to=orm['account.User']),
                      keep_default=False)

        # Adding field 'Article.photographer_name'
        db.add_column(u'magazine_article', 'photographer_name',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=128, blank=True),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'Article.author_name'
        db.delete_column(u'magazine_article', 'author_name')

        # Deleting field 'Article.photographer'
        db.delete_column(u'magazine_article', 'photographer_id')

        # Deleting field 'Article.photographer_name'
        db.delete_column(u'magazine_article', 'photographer_name')


    models = {
        u'account.user': {
            'Meta': {'object_name': 'User'},
            'about': ('django.db.models.fields.TextField', [], {'default': "''", 'blank': 'True'}),
            'activation_key': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '40', 'blank': 'True'}),
            'birth_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'city': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '255'}),
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'gender': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'hide_contacts': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'i_can': ('django.db.models.fields.TextField', [], {'default': "''", 'blank': 'True'}),
            'i_want': ('django.db.models.fields.TextField', [], {'default': "''", 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'interests': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['ihelpu.Topic']", 'symmetrical': 'False', 'blank': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'phone_number': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '18', 'blank': 'True'}),
            'photo': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'}),
            'web_site': ('django.db.models.fields.URLField', [], {'max_length': '200', 'blank': 'True'})
        },
        u'auth.group': {
            'Meta': {'object_name': 'Group'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        u'auth.permission': {
            'Meta': {'ordering': "(u'content_type__app_label', u'content_type__model', u'codename')", 'unique_together': "((u'content_type', u'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'ihelpu.topic': {
            'Meta': {'ordering': "('id',)", 'object_name': 'Topic'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '128'})
        },
        u'magazine.article': {
            'Meta': {'ordering': "('date_time',)", 'object_name': 'Article'},
            'author': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'articles'", 'null': 'True', 'to': u"orm['account.User']"}),
            'author_name': ('django.db.models.fields.CharField', [], {'max_length': '128', 'blank': 'True'}),
            'body': ('django.db.models.fields.TextField', [], {}),
            'cover_background': ('django.db.models.fields.CharField', [], {'default': "'#FFFFFF'", 'max_length': '8', 'blank': 'True'}),
            'cover_photo': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'blank': 'True'}),
            'date_time': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'home_photo': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_main': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'photographer': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'photosets'", 'null': 'True', 'to': u"orm['account.User']"}),
            'photographer_name': ('django.db.models.fields.CharField', [], {'max_length': '128', 'blank': 'True'}),
            'recommended_vacancies': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['vacancy.Vacancy']", 'symmetrical': 'False', 'blank': 'True'}),
            'summary': ('django.db.models.fields.CharField', [], {'max_length': '256', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'topics': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['ihelpu.Topic']", 'symmetrical': 'False', 'blank': 'True'})
        },
        u'magazine.comment': {
            'Meta': {'object_name': 'Comment'},
            'article': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'comments'", 'to': u"orm['magazine.Article']"}),
            'author': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['account.User']", 'null': 'True', 'blank': 'True'}),
            'body': ('django.db.models.fields.TextField', [], {}),
            'date_time': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'children'", 'null': 'True', 'to': u"orm['magazine.Comment']"})
        },
        u'vacancy.organization': {
            'Meta': {'object_name': 'Organization'},
            'address_line': ('django.db.models.fields.CharField', [], {'max_length': '128', 'blank': 'True'}),
            'city': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'contact_person': ('django.db.models.fields.CharField', [], {'max_length': '128', 'blank': 'True'}),
            'cover_background': ('django.db.models.fields.CharField', [], {'default': "'#FFFFFF'", 'max_length': '8', 'blank': 'True'}),
            'cover_photo': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'logo': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'blank': 'True'}),
            'phone_number': ('django.db.models.fields.CharField', [], {'max_length': '18', 'blank': 'True'}),
            'slogan': ('django.db.models.fields.CharField', [], {'max_length': '384', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'topics': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['ihelpu.Topic']", 'symmetrical': 'False', 'blank': 'True'}),
            'web_site': ('django.db.models.fields.URLField', [], {'max_length': '200', 'blank': 'True'}),
            'zip_code': ('django.db.models.fields.CharField', [], {'max_length': '6', 'blank': 'True'})
        },
        u'vacancy.vacancy': {
            'Meta': {'object_name': 'Vacancy'},
            'cover_background': ('django.db.models.fields.CharField', [], {'default': "'#FFFFFF'", 'max_length': '8', 'blank': 'True'}),
            'cover_photo': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_continuous': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'organization': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'vacancies'", 'to': u"orm['vacancy.Organization']"}),
            'recommended_vacancies': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'recommended_vacancies_rel_+'", 'blank': 'True', 'to': u"orm['vacancy.Vacancy']"}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'topics': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['ihelpu.Topic']", 'symmetrical': 'False'}),
            'volunteers': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'vacancies'", 'symmetrical': 'False', 'to': u"orm['account.User']"})
        }
    }

    complete_apps = ['magazine']