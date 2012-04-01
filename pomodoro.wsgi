import os, sys
sys.path.append('/home/sajan/Django-1.3.1/')
sys.path.append('/home/sajan/dev/python/django/')
sys.path.append('/home/sajan/dev/python/django/pomodoro/')
sys.path.append('/home/sajan/dev/python/django/pomodoro/pomsite/')
sys.path.append('/home/sajan/dev/python/django/djangoutils/src/')

os.environ['DJANGO_SETTINGS_MODULE'] = 'production_settings'
os.environ['MPLCONFIGDIR']='/home/sajan/.matplotlib'
import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()
