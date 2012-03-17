# Django settings for pomsite project.

DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    # ('Your Name', 'your_email@domain.com'),
)

MANAGERS = ADMINS

DATABASE_ENGINE = 'postgresql_psycopg2'           # 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
DATABASE_NAME = 'pomdb'             # Or path to database file if using sqlite3.
DATABASE_USER = 'sajan'             # Not used with sqlite3.
DATABASE_PASSWORD = ''         # Not used with sqlite3.
DATABASE_HOST = ''             # Set to empty string for localhost. Not used with sqlite3.
DATABASE_PORT = ''             # Set to empty string for default. Not used with sqlite3.


#login url added by sajan
LOGIN_URL='/pomlog/account/login/'
LOGIN_REDIRECT_URL='/pomlog/entries/'


# mail server
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_HOST_USER = 'pomodoroadmn@gmail.com'
EMAIL_HOST_PASSWORD = 'agameofcode'
EMAIL_USE_TLS = True
DEFAULT_FROM_EMAIL = 'pomodoroadmn@gmail.com'
#EMAIL_BACKEND='django.core.mail.backends.console.EmailBackend'


# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'Asia/Calcutta'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

SITE_ID = 2

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
#MEDIA_ROOT = ''
MEDIA_ROOT = '/home/sajan/dev/python/django/pomodoro/pomsite/media/pomlogger/'
# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = '/site_media/'

IMAGE_FOLDER_PATH = '/home/sajan/dev/python/django/pomodoro/pomsite/media/pomlogger/img'

LOGFILE_NAME = '/home/sajan/dev/python/django/pomodoro/pomodorolog.txt'


#Pagination-number of entries to be listed per page
PAGINATE_BY=10
#chart type to be created
CHART_TYPE="bar"

#barchart related constant values
BAR_WIDTH = .2
PLOT_OFFSET = .3
BAR_COLOR = '#52E4FF'
LABEL_COLOR = 'blue'
TITLE_COLOR ='black'
REPORT_IMG_FMT = 'png'
REPORT_DOC_FMT = 'pdf'
FIGURE_WIDTH_SCALE_FACTOR = 8
YSTEP_FACTOR = 10
# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = '/media/'

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'q3!2+$t%263z%q#5(f)%0o-hh%_7zttp9bz*m5fr+mtxb9#+^h'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.load_template_source',
    'django.template.loaders.app_directories.load_template_source',
#     'django.template.loaders.eggs.load_template_source',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
)

ROOT_URLCONF = 'pomsite.urls'

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    '/home/sajan/dev/python/django/pomodoro/pomsite/pomlogger/pomlogtemplates',
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.admin',
    'registration',
    'pomlogger',
)
#account activation open for a week
ACCOUNT_ACTIVATION_DAYS = 2
