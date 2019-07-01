"""
Django settings for university_management_service project.

Generated by 'django-admin startproject' using Django 2.1.7.

For more information on this file, see
https://docs.djangoproject.com/en/2.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.1/ref/settings/
"""

import os
from django_replicated.settings import *

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '*55f&3o6o(!r!p+$7kth1i4idv2fden6dve=d51zb$xfu1x=8n'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*']


# Application definition

INSTALLED_APPS = [
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    #override django's admin
    'university',
    'django.contrib.admin',
    'daterange_filter'
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'university_management_service.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'university.context_processors.request_userData',
            ],
        },
    },
]

WSGI_APPLICATION = 'university_management_service.wsgi.application'


# Database
# https://docs.djangoproject.com/en/2.1/ref/settings/#databases


DATABASES = {
    'default': {
        'HOST': '127.0.0.1',
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'wyvern',
        'USER': os.getenv('DATABASE_USER'),
        'PASSWORD': os.getenv('DATABASE_PASSWORD'),
        'PORT': '3306'
    },
    # 'slave1': {
    #     'HOST': '35.189.116.95',
    #     'ENGINE': 'django.db.backends.mysql',
    #     'NAME': 'wyvern',
    #     'USER': os.getenv('DATABASE_USER'),
    #     'PASSWORD': os.getenv('DATABASE_PASSWORD'),
    #     'PORT': '3306'
    # }
}

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
        'LOCATION': 'memcached-service.memcached.svc.cluster.local'
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/2.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


#STATIC_URL = '/static/'
STATIC_URL = 'https://storage.googleapis.com/wyvern-bucket/'
STATIC_ROOT = os.path.join(BASE_DIR, 'university/static')
MIGRATIONS_DATA_ROOT = os.path.join(BASE_DIR, 'university/migrations_data')

# REPLICATED_DATABASE_SLAVES = ['slave1']
# DATABASE_ROUTERS = ['django_replicated.router.ReplicationRouter']
# REPLICATED_DATABASE_DOWNTIME = 20