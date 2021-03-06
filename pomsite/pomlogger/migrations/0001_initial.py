# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'PomCategory'
        db.create_table('pomlogger_pomcategory', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=50)),
            ('description', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('slug', self.gf('django.db.models.fields.SlugField')(max_length=50)),
        ))
        db.send_create_signal('pomlogger', ['PomCategory'])

        # Adding M2M table for field users on 'PomCategory'
        db.create_table('pomlogger_pomcategory_users', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('pomcategory', models.ForeignKey(orm['pomlogger.pomcategory'], null=False)),
            ('user', models.ForeignKey(orm['auth.user'], null=False))
        ))
        db.create_unique('pomlogger_pomcategory_users', ['pomcategory_id', 'user_id'])

        # Adding model 'PomEntry'
        db.create_table('pomlogger_pomentry', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('today', self.gf('django.db.models.fields.DateField')(default=datetime.date.today)),
            ('start_time', self.gf('django.db.models.fields.TimeField')(null=True)),
            ('end_time', self.gf('django.db.models.fields.TimeField')(null=True)),
            ('description', self.gf('django.db.models.fields.TextField')()),
            ('author', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], null=True)),
        ))
        db.send_create_signal('pomlogger', ['PomEntry'])

        # Adding M2M table for field sharedwith on 'PomEntry'
        db.create_table('pomlogger_pomentry_sharedwith', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('pomentry', models.ForeignKey(orm['pomlogger.pomentry'], null=False)),
            ('user', models.ForeignKey(orm['auth.user'], null=False))
        ))
        db.create_unique('pomlogger_pomentry_sharedwith', ['pomentry_id', 'user_id'])

        # Adding M2M table for field categories on 'PomEntry'
        db.create_table('pomlogger_pomentry_categories', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('pomentry', models.ForeignKey(orm['pomlogger.pomentry'], null=False)),
            ('pomcategory', models.ForeignKey(orm['pomlogger.pomcategory'], null=False))
        ))
        db.create_unique('pomlogger_pomentry_categories', ['pomentry_id', 'pomcategory_id'])


    def backwards(self, orm):
        # Deleting model 'PomCategory'
        db.delete_table('pomlogger_pomcategory')

        # Removing M2M table for field users on 'PomCategory'
        db.delete_table('pomlogger_pomcategory_users')

        # Deleting model 'PomEntry'
        db.delete_table('pomlogger_pomentry')

        # Removing M2M table for field sharedwith on 'PomEntry'
        db.delete_table('pomlogger_pomentry_sharedwith')

        # Removing M2M table for field categories on 'PomEntry'
        db.delete_table('pomlogger_pomentry_categories')


    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'ordering': "('content_type__app_label', 'content_type__model', 'codename')", 'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'pomlogger.pomcategory': {
            'Meta': {'object_name': 'PomCategory'},
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '50'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '50'}),
            'users': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.User']", 'symmetrical': 'False'})
        },
        'pomlogger.pomentry': {
            'Meta': {'object_name': 'PomEntry'},
            'author': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True'}),
            'categories': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['pomlogger.PomCategory']", 'symmetrical': 'False'}),
            'description': ('django.db.models.fields.TextField', [], {}),
            'end_time': ('django.db.models.fields.TimeField', [], {'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'sharedwith': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "'sharedwith'", 'null': 'True', 'to': "orm['auth.User']"}),
            'start_time': ('django.db.models.fields.TimeField', [], {'null': 'True'}),
            'today': ('django.db.models.fields.DateField', [], {'default': 'datetime.date.today'})
        }
    }

    complete_apps = ['pomlogger']