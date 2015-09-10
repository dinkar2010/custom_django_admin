"""
Django settings for movincart project.

For more information on this file, see
https://docs.djangoproject.com/en/1.7/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.7/ref/settings/
"""
from settings_local import *
# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
from django.conf.global_settings import TEMPLATE_CONTEXT_PROCESSORS

BASE_DIR = os.path.dirname(os.path.dirname(__file__))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.7/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '1k8@-h&7alm+xdukek_cka&m$mskovtg$yrs9=3cz*g%k=-+t3'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

TEMPLATE_DEBUG = True

ALLOWED_HOSTS = ['*']


INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'suit',
    'django.contrib.admin',
    'app',
    'geoposition',
    'django.contrib.gis',
    'tastypie',
    'tastypie_swagger',
    'nested_inline',
    'django_crontab',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'movincart.urls'

WSGI_APPLICATION = 'movincart.wsgi.application'

CRONJOBS = [
('*/10 * * * *', 'app.utils.delivery_confirmation_notification.send_notifications')
]
# Database
# https://docs.djangoproject.com/en/1.7/ref/settings/#databases

# Internationalization
# https://docs.djangoproject.com/en/1.7/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Asia/Calcutta'

USE_I18N = True

USE_L10N = True

USE_TZ = False


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.7/howto/static-files/

STATIC_URL = '/static/'

STATICFILES_DIRS = (os.path.join(os.path.dirname(__file__), 'static'),)

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    #    'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

SUIT_CONFIG = {
    'ADMIN_NAME': 'MovinCart',
    'MENU': (
        'sites',
    {'app': 'app', 'label': 'MovinCart App', 'icon':'icon-leaf'},
    {'app': 'auth', 'label': 'Authorization', 'icon':'icon-lock'},
    {'app': 'tastypie', 'label': 'Tastypie', 'icon':'icon-ban-circle'},
    {'app': 'default', 'label': 'System Settings', 'icon':'icon-ban-circle'},
    # {'app': 'registration', 'label': 'Registration Internals', 'icon':'icon-ban-circle'},
    ),
    'MENU_OPEN_FIRST_CHILD': False
}

TEMPLATE_CONTEXT_PROCESSORS += ('django.core.context_processors.request',)
TASTYPIE_DEFAULT_FORMATS = ['json']
TEMPLATE_DIRS = [
os.path.join(BASE_DIR, 'templates')
]
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
)
