from pathlib import Path
import django
import warnings
from django.conf import settings
from django.contrib.messages import constants as messages

import os
from decouple import config

import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration

_SENTINEL = ...

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = config("SECRET_KEY", default="development_weak_secret_key")

DEBUG = config('DEBUG', default=False, cast=bool)

ALLOWED_HOSTS = ['127.0.0.1',
                'droplinkfy.herokuapp.com',
                'qa.droplinkfy.com',
                'qa-droplinkfy.herokuapp.com',
                'app.droplinkfy.com',
                'dev.droplinkfy.com',
                'dev-droplinkfy.herokuapp.com',
                'front-droplinkfy.herokuapp.com',
                'https://droplinkfy-nginx.herokuapp.com']

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_crontab',
    'django_cpf_cnpj',
    'loginas',
    'shopee',
    'gtm',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'debug_toolbar.middleware.DebugToolbarMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'session_security.middleware.SessionSecurityMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
]

MESSAGE_TAGS = {
    messages.ERROR: 'danger',
}

GOOGLE_ANALYTICS_ID = config("GOOGLE_ANALYTICS_ID", default=_SENTINEL)

if GOOGLE_ANALYTICS_ID is _SENTINEL and not DEBUG:
    warnings.warn("GOOGLE_ANALYTICS_ID is not set. "
                  "Google Analytics will not be enabled.")

ROOT_URLCONF = 'project.urls'

CONSULT_PRODUCT_TIMEOUT = config("CONSULT_PRODUCT_TIMEOUT", 10)

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
                "shopee.context_processors.get_user_news",
                "shopee.context_processors.get_alerts",
                "shopee.context_processors.get_sentry_dsn",
                "shopee.context_processors.get_enviroment_variables",
                'django.contrib.messages.context_processors.messages',
                "shopee.context_processors.google_analytics",
            ],
        },
    },
]

WSGI_APPLICATION = 'project.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        "NAME": config("DB_NAME", default=os.path.join(BASE_DIR, "db.sqlite3")),
        "USER": config("DB_USER", default="user"),
        "HOST": config("DB_HOST", default="localhost"),
        "PORT": config("DB_PORT", default="5432"),
        "PASSWORD": config("DB_PASSWORD", default="nave"),
    },
    'replica': {
        'ENGINE': 'django.db.backends.postgresql',
        "NAME": config("DB_REPLICA_NAME"),
        "USER": config("DB_REPLICA_USER"),
        "HOST": config("DB_REPLICA_HOST"),
        "PORT": config("DB_REPLICA_PORT", default="5432"),
        "PASSWORD": config("DB_REPLICA_PASSWORD"),
    }
}

DATABASE_ROUTERS = [
    "shopee.db_routers.ReplicaRouter",
]

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

AUTHENTICATION_BACKENDS = [
    'shopee.backends.EmailBackend',
]

LANGUAGE_CODE = 'pt-BR'

TIME_ZONE = 'America/Sao_Paulo'

USE_I18N = True

USE_L10N = True

USE_TZ = True

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

STATICFILES_DIRS = (
    os.path.join(BASE_DIR, 'static'),
)

LOGIN_REDIRECT_URL='/login'

SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SECURE_SSL_REDIRECT = config('SECURE_SSL_REDIRECT', default=False, cast=bool)
CSRF_TRUSTED_ORIGINS = [
    'https://droplinkfy-nginx.herokuapp.com',
    'droplinkfy-nginx.herokuapp.com',
    'droplinkfy-nginx.herokuapp.com/login',
    'https://droplinkfy-nginx.herokuapp.com/login/'
    ]

RAVEN_CONFIG = {
    'dsn': config('SENTRY_DSN'),
}

DEBUG = config('DEBUG', default=False, cast=bool)
SESSION_COOKIE_SAMESITE = None
SESSION_SECURITY_EXPIRE_AFTER=config('SESSION_SECURITY_EXPIRE_AFTER', default=3600, cast=int)
SESSION_SECURITY_INSECURE = True

GOOGLE_TAG_ID = config('GOOGLE_TAG_ID')

#SMTP Configuration
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = config('EMAIL_HOST')
EMAIL_PORT = config('EMAIL_PORT')
EMAIL_USE_TLS= config('DEBUG', default=True, cast=bool)
EMAIL_HOST_USER = config('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD')
DEFAULT_FROM_EMAIL = config('DEFAULT_FROM_EMAIL')

# ENV
REPORT_CHECK_STATUS_INTERVAL = config('REPORT_CHECK_STATUS_INTERVAL', default=3000, cast=int)
REPORT_TIMEOUT_MS = config('REPORT_TIMEOUT_MS', default=30000, cast=int)
VENDORUSERCREATE_SMS_COUNTER = config("VENDORUSERCREATE_SMS_COUNTER", 60)
NOTION_VENDOR_USERS_URL = config("NOTION_VENDOR_USERS_URL")
NOTION_SHOPIFY_URL = config("NOTION_SHOPIFY_URL")
NOTION_PRODUCT_URL = config("NOTION_PRODUCT_URL")
NOTION_ACCOUNT_URL = config("NOTION_ACCOUNT_URL")
NOTION_NEWS_URL = config("NOTION_NEWS_URL")
NOTION_ORDER_URL = config("NOTION_ORDER_URL")
CANCEL_SLACK_WEBHOOK = config("CANCEL_SLACK_WEBHOOK", "https://hooks.slack.com/services/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")
CANCEL_SLACK_WEBHOOK_ICON = config("CANCEL_SLACK_WEBHOOK", "https://images.assets-landingi.com/UpFSzAEkrKgvGc9C/cube.png")
CANCEL_SUBSCRIPTION_MESSAGE = config("CANCEL_SUBSCRIPTION_MESSAGE", "Sua solicitação de cancelamento será processada em até 48 horas.")
LIMIT_SYNC_PRODUCTS_REQUEST = config("LIMIT_SYNC_PRODUCTS_REQUEST", cast=int)
NOTION_ORDER_URL = config("NOTION_ORDER_URL")
REST_GATEWAY_CONSULT_PRODUCT = config("REST_GATEWAY_CONSULT_PRODUCT")
REST_GATEWAY_CONSULT_PRODUCT_API_KEY = config("REST_GATEWAY_CONSULT_PRODUCT_API_KEY")
PHONE_VALIDATION_ERROR_DDI_MSG = config("PHONE_VALIDATION_ERROR_DDI_MSG","DDI inválido (Lembre-se de adicionar +55 ao número de telefone).")
PHONE_VALIDATION_ERROR_DDD_MSG = config("PHONE_VALIDATION_ERROR_DDD_MSG", "DDD do telefone inválido.")
PHONE_VALIDATION_ERROR_PHONE_MSG = config("PHONE_VALIDATION_ERROR_PHONE_MSG", "Telefone inválido."),
FILL_ALL_FIELDS_VALIDATION_MSG = config("FILL_ALL_FIELDS_VALIDATION_MSG","Error: Preencha todos os campos para continuar.")
FREE_SHIPPING_MESSAGE = config("FREE_SHIPPING_MESSAGE")
PRICE_MESSAGE = config("PRICE_MESSAGE")
FREE_SHIPPING_MESSAGE = config('FREE_SHIPPING_MESSAGE')
AFFILIATES_URL = config('AFFILIATES_URL')
STRIPE_PRODUCT_PRICE = config("STRIPE_PRODUCT_PRICE")
AFFILIATE_STRIPE_PRODUCT_PRICE = config("AFFILIATE_STRIPE_PRODUCT_PRICE")
CRISP_WEBSITE_ID = config("CRISP_WEBSITE_ID")
SENTRY_DSN = config('SENTRY_DSN')
MANUAL_NOTION_URL = config("MANUAL_NOTION_URL")
SUPORTE_NOTION_URL = config("SUPORTE_NOTION_URL")
AFFILIATES_URL = config("AFFILIATES_URL")
BONANZA_URL = config("BONANZA_URL")
BLAZING_URL = config("BLAZING_URL")
ATUALIZACAO_V2 = config("ATUALIZACAO_V2")
MANUAL_ASSINATURA = config("MANUAL_ASSINATURA")
SMS_RUSSO_URL = config("SMS_RUSSO_URL")
MANUAL_FATURAMENTO = config("MANUAL_FATURAMENTO")
LIMIT_MANUAL_PAY_REQUEST = config("LIMIT_MANUAL_PAY_REQUEST", cast=int)
REST_GATEWAY_CREATE_USERSHPOPEE = config("REST_GATEWAY_CREATE_USERSHPOPEE")
REST_GATEWAY_CREATE_USERSHOPEE_ORDER_KEY = config("REST_GATEWAY_CREATE_USERSHOPEE_ORDER_KEY")
REST_GATEWAY_CREATE_USERSSHOPEES = config("REST_GATEWAY_CREATE_USERSSHOPEES")
REST_GATEWAY_CREATE_USERSSHOPEES_API_KEY = config("REST_GATEWAY_CREATE_USERSSHOPEES_API_KEY")
API_GATEWAY_UPSERT_PRODUCTS = config("API_GATEWAY_UPSERT_PRODUCTS")
API_GATEWAY_MAKE_ORDER = config("API_GATEWAY_MAKE_ORDER")
REST_GATEWAY_CANCEL_ORDER = config("REST_GATEWAY_CANCEL_ORDER")
REST_GATEWAY_CANCEL_ORDER_KEY = config("REST_GATEWAY_CANCEL_ORDER_KEY")
REST_GATEWAY_CREATE_USERSHOPEE_GOOGLE = config("REST_GATEWAY_CREATE_USERSHOPEE_GOOGLE")
REST_GATEWAY_CREATE_USERSHOPEE_GOOGLE_ORDER_KEY = config("REST_GATEWAY_CREATE_USERSHOPEE_GOOGLE_ORDER_KEY")
REST_GATEWAY_CREATE_USERSHPOPEE_V3 = config("REST_GATEWAY_CREATE_USERSHPOPEE_V3")
REST_GATEWAY_CREATE_USERSHOPEE_V3_ORDER_KEY = config("REST_GATEWAY_CREATE_USERSHOPEE_V3_ORDER_KEY")
REST_GATEWAY_CREATE_USERSHOPEE_EDITPHONE = config("REST_GATEWAY_CREATE_USERSHOPEE_EDITPHONE")
REST_GATEWAY_CREATE_USERSHOPEE_EDITPHONE_ORDER_KEY = config("REST_GATEWAY_CREATE_USERSHOPEE_EDITPHONE_ORDER_KEY")
REST_GATEWAY_CREATE_VALIDATEUSERSHOPEE = config("REST_GATEWAY_CREATE_VALIDATEUSERSHOPEE")
REST_GATEWAY_CREATE_VALIDATEUSERSHOPEE_API_KEY = config("REST_GATEWAY_CREATE_VALIDATEUSERSHOPEE_API_KEY")
REST_GATEWAY_CREATE_RESENDSMSOPT = config("REST_GATEWAY_CREATE_RESENDSMSOPT")
REST_GATEWAY_CREATE_RESENDSMSOPT_API_KEY = config("REST_GATEWAY_CREATE_RESENDSMSOPT_API_KEY")
REST_GATEWAY_GENERATE_REPORT = config("REST_GATEWAY_GENERATE_REPORT")
REST_GATEWAY_GENERATE_REPORT_API_KEY = config("REST_GATEWAY_GENERATE_REPORT_API_KEY")
REST_GATEWAY_SECONDPART_CREATE_USERSHPOPEE_V3 = config("REST_GATEWAY_SECONDPART_CREATE_USERSHPOPEE_V3")
REST_GATEWAY_SECONDPART_CREATE_USERSHOPEE_V3_ORDER_KEY = config("REST_GATEWAY_SECONDPART_CREATE_USERSHOPEE_V3_ORDER_KEY")
REST_GATEWAY_CREATE_USERSHOPEE_SECONDGOOGLE = config("REST_GATEWAY_CREATE_USERSHOPEE_SECONDGOOGLE")
REST_GATEWAY_CREATE_USERSHOPEE_SECONDGOOGLE_ORDER_KEY = config("REST_GATEWAY_CREATE_USERSHOPEE_SECONDGOOGLE_ORDER_KEY")
REST_GATEWAY_CREATE_WEBHOOKS = config("REST_GATEWAY_CREATE_WEBHOOKS")
REST_GATEWAY_CREATE_WEBHOOKS_API_KEY = config("REST_GATEWAY_CREATE_WEBHOOKS_API_KEY")
REST_GATEWAY_DELETE_WEBHOOKS = config("REST_GATEWAY_DELETE_WEBHOOKS")
REST_GATEWAY_DELETE_WEBHOOKS_API_KEY = config("REST_GATEWAY_DELETE_WEBHOOKS_API_KEY")
REST_GATEWAY_MANUAL_RETRY_PERCENTAGE = config("REST_GATEWAY_MANUAL_RETRY_PERCENTAGE")
REST_GATEWAY_MANUAL_RETRY_PERCENTAGE_API_KEY = config("REST_GATEWAY_MANUAL_RETRY_PERCENTAGE_API_KEY")
REST_GATEWAY_MANUAL_RETRY_PERCENTAGE = config("REST_GATEWAY_MANUAL_RETRY_PERCENTAGE")
REST_GATEWAY_MANUAL_RETRY_PERCENTAGE_API_KEY = config("REST_GATEWAY_MANUAL_RETRY_PERCENTAGE_API_KEY")
STRIPE_API_KEY = config("STRIPE_API_KEY")
STRIPE_PUBLIC_KEY = config("STRIPE_PUBLIC_KEY")

if config('DEBUG', default=True, cast=bool):
    sentry_sdk.init(
        dsn=config('SENTRY_DSN'),
        integrations=[DjangoIntegration()],
        traces_sample_rate=1.0
    )
else:
    sentry_sdk.init(
        dsn=config('SENTRY_DSN'),
        integrations=[DjangoIntegration()],
        send_default_pii=True,
        traces_sample_rate=config("TRACES_SAMPLER", default=1)
    ) 
