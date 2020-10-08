import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.10/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '@7w5)c63v6yzmj@=d9$($3xao1tjw667h4(kof#2b6g=3)p7-r'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'rest_framework.authtoken',
    'tinymce',
    'django_filters',
    'rest_auth',
    'api',
    'main',
    'corsheaders',
    'admin_reorder',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'admin_reorder.middleware.ModelAdminReorder',

]


ADMIN_REORDER = (
    # Keep original label and models
    # 'sites',

    # # Rename app
    # {'app': 'auth', 'label': 'Authorisation'},
    #
    # # Reorder app models
    # {'app': 'auth', 'models': ('auth.User', 'auth.Group')},
    #
    # # Exclude models
    # {'app': 'auth', 'models': ('auth.User', )},
    #
    # # Cross-linked models
    # {'app': 'auth', 'models': ('auth.User', 'sites.Site')},
    #
    # # models with custom name
    # {'app': 'main', 'label': 'Галерея', 'models': (
    #     'main.Gallery',
    #     'main.VideoGallery',
    # )},

    # {'app': 'main', 'label': 'Основное меню', 'models': (
    #     'main.User',
    #     # 'main.Feedback',
    # )},

    {'app': 'main', 'label': 'Справочники', 'models': (
        'main.User',
        'main.Field',
        'main.Well',
        'main.Constant',
    )},

    {'app': 'main', 'label': 'Меню ИСУ', 'models': (
        'main.Depression',
        # 'main.TS',
        # 'main.GSM',
        'main.ProdProfile',
        'main.Dynamogram',
        'main.Imbalance',
        'main.ImbalanceHistoryAll',
        'main.SumWellInField',
        # 'authtoken.Token'
    )},

    {'app': 'main', 'label': 'Меню ГТМ', 'models': (
        'main.WellMatrix',
        'main.WellEvents',
        'main.Events',
        'main.Recommendation',
        # 'main.TS',
        # 'main.GSM',
        'main.FieldMatrix'
        # 'authtoken.Token'
    )},
    {'app': 'main', 'label': 'Меню ПРС', 'models': (
        'main.PrsDevice',
    )},
)


CORS_ORIGIN_ALLOW_ALL = True
CORS_ALLOW_CREDENTIALS = True
ALLOWED_HOSTS = ['*']

ROOT_URLCONF = 'system.urls'

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
            ],
        },
    },
]

WSGI_APPLICATION = 'system.wsgi.application'


GOOGLE_RECAPTCHA_SECRET_KEY = '6Lenn6UUAAAAAJQaQUt4aLxDGXY2PUbQuOLhYLJf'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    },
    'OPTIONS': {
        'timeout': 40,
    }
}


# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.postgresql_psycopg2',
#         'NAME': 'cmdb',
#         'USER': 'cm_user',
#         'PASSWORD': 'cm_pass',
#         'HOST': 'localhost',
#         'PORT': '',
#     }
# }



TINYMCE_DEFAULT_CONFIG = {
    'plugins': "paste",
    'paste_remove_styles': 'true',
    'paste_remove_styles_if_webkit': 'true',
    'paste_strip_class_attributes': 'all',
    'theme': 'advanced',
    'theme_advanced_buttons1': 'bold,italic,underline',
    'theme_advanced_resizing': True,
}

# Password validation
# https://docs.djangoproject.com/en/1.10/ref/settings/#auth-password-validators

# AUTH_PASSWORD_VALIDATORS = [
#     {
#         'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
#     },
#     {
#         'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
#     },
#     {
#         'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
#     },
#     {
#         'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
#     },
# ]

LANGUAGES = [
    ('ru', ('Русский')),
]

# Internationalization
# https://docs.djangoproject.com/en/1.10/topics/i18n/

LANGUAGE_CODE = 'ru-RU'

TIME_ZONE = 'Asia/Almaty'

USE_I18N = True

USE_L10N = True

USE_TZ = True

LOCALE_PATHS = (
    os.path.join(BASE_DIR, 'locale'),
)


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.10/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = '/static/cm/'

MEDIA_URL = '/media/'
MEDIA_ROOT = '/media/cm/'

AUTH_USER_MODEL = 'main.User'


REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.TokenAuthentication',
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.BasicAuthentication',
    ),
}


MAX_UPLOAD_SIZE = "524288000"

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_USE_TLS = True
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_HOST_USER = '123@gmail.com'
EMAIL_HOST_PASSWORD = 'pos12345'
EMAIL_PORT = 587