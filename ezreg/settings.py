"""
Django settings for ezreg project.

Generated by 'django-admin startproject' using Django 1.8.4.

For more information on this file, see
https://docs.djangoproject.com/en/1.8/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.8/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
from django.conf.global_settings import AUTHENTICATION_BACKENDS

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.8/howto/deployment/checklist/



# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'tinymce',
    'ezreg',
    'crispy_forms',
    'rest_framework',
    'django_filters',
    'rest_framework_filters',
    'datetimewidget',
    'mailqueue',
    'django_json_forms',
    'django_bleach',
    'cas',
    'compressor',
    'django_logger',
)

MIDDLEWARE = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
#     'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.security.SecurityMiddleware',
)



ROOT_URLCONF = 'ezreg.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'ezreg.context_processors.permissions_processor',
                'ezreg.context_processors.settings_processor'
            ],
        },
    },
]

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    # other finders..
    'compressor.finders.CompressorFinder',
)

WSGI_APPLICATION = 'ezreg.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.8/ref/settings/#databases



# Internationalization
# https://docs.djangoproject.com/en/1.8/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'America/Los_Angeles'

USE_I18N = True

USE_L10N = True

# USE_TZ = True
USE_TZ = False # quick fix to try resolving "database connection isn't set to UTC" assertion error after upgrade to django 2.x

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.8/howto/static-files/


STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR,'static')

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR,'media')

FILES_ROOT = os.path.join(BASE_DIR,'files')


DJANGO_JSON_FORMS_UPLOAD_DIRECTORY = os.path.join(FILES_ROOT,'form_files') 
# DJANGO_JSON_FORMS_GET_UPLOAD_PATH

TINYMCE_DEFAULT_CONFIG = {
    "theme": "silver",
    "height": 500,
    "menubar": False,
    "plugins": "advlist,autolink,lists,link,image,charmap,print,preview,anchor,"
    "searchreplace,visualblocks,code,fullscreen,insertdatetime,media,table,paste,"
    "code,help,wordcount",
    "toolbar": "undo redo | formatselect | "
    "bold italic backcolor | alignleft aligncenter "
    "alignright alignjustify | bullist numlist outdent indent | "
    "removeformat | help",
    "plugins": [
        'advlist autolink link image lists charmap print preview hr anchor pagebreak',
        'searchreplace wordcount visualblocks code fullscreen insertdatetime media nonbreaking',
        'table emoticons template paste help'
    ],
  "toolbar": 'undo redo | styleselect | bold italic | alignleft aligncenter alignright alignjustify | bullist numlist outdent indent | link image | print preview media fullscreen | forecolor backcolor emoticons | help',
  "menubar": 'file edit view insert format tools table help',
  "content_style": 'body { font-family:Helvetica,Arial,sans-serif; font-size:14px }'
}


ANONYMOUS_USER_ID = None

CRISPY_TEMPLATE_PACK = 'bootstrap3'

REST_FRAMEWORK = {
    'DEFAULT_FILTER_BACKENDS': ('django_filters.rest_framework.DjangoFilterBackend','rest_framework.filters.OrderingFilter','rest_framework.filters.SearchFilter',),
    'DEFAULT_PAGINATION_CLASS': 'ezreg.api.pagination.ResultsSetPagination',
}


# Which HTML tags are allowed
BLEACH_ALLOWED_TAGS = [
    "h1", "h2", "h3", "h4", "h5", "h6",
    "b", "i", "strong", "em", "tt",
    "p", "br",
    "blockquote", "code", "hr",
    "ul", "ol", "li", "dd", "dt",
    "img",
    "table", "thead", "tbody", "tfoot", "tr", "th", "td",
    "a", "iframe"
]

# Which HTML attributes are allowed
BLEACH_ALLOWED_ATTRIBUTES = ['href', 'title', 'style','src','width','height']

# Which CSS properties are allowed in 'style' attributes (assuming
# style is an allowed attribute)
BLEACH_ALLOWED_STYLES = [
    'font-family', 'font-weight', 'text-decoration', 'font-variant', 'text-align', 'text-decoration']

# Strip unknown tags if True, replace with HTML escaped characters if
# False
BLEACH_STRIP_TAGS = True

# Strip comments, or leave them in.
BLEACH_STRIP_COMMENTS = False

COMPRESS_ENABLED = True

HEADER_TEXT = 'Genome Center Registration'

SERVICE_CHARGE_PERCENT = 3.0
CREDIT_CARD_CHARGE_PERCENT = 2.75

MESSAGES = []

# DEFAULT_EXCEPTION_REPORTER_FILTER = 'ezreg.debug.LimitedExceptionReporterFilter'

REFUND_ADMIN_EMAILS = []

try:
    from ezreg.config import *
except:
    print('No config.py file')

