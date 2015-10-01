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

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '2_mcoc_%_g#d*!3hbqbwnqb$id9-_eha@&&2zhju^o7a3@819m'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []

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
    'guardian',
    'crispy_forms',
    'rest_framework',
    'datetimewidget',
    'mailqueue',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.security.SecurityMiddleware',
)

AUTHENTICATION_BACKENDS += (
    'guardian.backends.ObjectPermissionBackend',
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
            ],
        },
    },
]

WSGI_APPLICATION = 'ezreg.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.8/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'ezreg',
        'USER': 'dev',
        'PASSWORD': 'dev',
        'HOST': '127.0.0.1',
        'PORT': '5432',
    }
}

# Internationalization
# https://docs.djangoproject.com/en/1.8/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'America/Los_Angeles'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.8/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR,'static')

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR,'media')

FILES_ROOT = os.path.join(BASE_DIR,'files')


TINYMCE_DEFAULT_CONFIG = {
    'theme' : 'advanced',
#     'theme_advanced_buttons1' : 'bold,italic,underline,separator,bullist,numlist,separator,link,unlink,header1,header2',
#     'theme_advanced_buttons2' : '',
#     'theme_advanced_buttons3' : '',
    'theme_advanced_toolbar_location' : 'top',
    'theme_advanced_toolbar_align': 'left',
    'paste_text_sticky': True,
    'paste_text_sticky_default' : True,
    'valid_styles' : 'font-weight,font-style,text-decoration',
}

ANONYMOUS_USER_ID = None

CRISPY_TEMPLATE_PACK = 'bootstrap3'

REST_FRAMEWORK = {
    'DEFAULT_FILTER_BACKENDS': ('rest_framework.filters.DjangoFilterBackend','rest_framework.filters.OrderingFilter','rest_framework.filters.SearchFilter',),
    'DEFAULT_PAGINATION_CLASS': 'ezreg.api.pagination.ResultsSetPagination',
}



PAYMENT_PROCESSORS = [
    'ezreg.payment.dafis.processor.DafisPaymentProcessor',
    'ezreg.payment.touchnet.processor.TouchnetPaymentProcessor',
]

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.ucdavis.edu'