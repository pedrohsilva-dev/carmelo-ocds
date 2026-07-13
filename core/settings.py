from pathlib import Path
import os

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/6.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "django-insecure-lm#u=3l65fm-zwh7tc!)iho4b0r@lor-q2iy8550$1c4mckh)="

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ["*"]


# Application definition

INSTALLED_APPS = [
    "jazzmin",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rolepermissions",
    "compressor",
    "django_extensions",
    # MYAPPS
    "base",
    "carmel",
    "members",
    "votes",
    "contributions",
    "accounts",
]


LANGUAGE_CODE = "pt-br"
USE_I18N = True

AUTH_USER_MODEL = "members.Member"

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "base.middlewares.PrefetchUserPermissionsMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "base.middlewares.HtmxMessagesMiddleware",
]

LOGIN_REDIRECT_URL = "/accounts/login"

ROOT_URLCONF = "core.urls"

if DEBUG:
    idx = MIDDLEWARE.index("django.middleware.security.SecurityMiddleware")
    MIDDLEWARE.insert(idx + 1, "django_devbar.DevBarMiddleware")

if DEBUG:
    DEVBAR = {
        "POSITION": "bottom-right",  # bottom-right (default), bottom-left, top-right, top-left
        "SHOW_BAR": None,  # follows DEBUG; set True/False to override
        "ENABLE_DEVTOOLS_DATA": None,  # follows DEBUG; set True/False to override
        "DEVTOOLS_HEADER_MAX_BYTES": 6144,  # max bytes for DevBar-Data header payload
        "DEVTOOLS_MAX_QUERIES": None,  # optional hard cap for q/dup entries sent to DevTools
    }
    GRAPH_MODELS = {
        "group_models": True,
        "inheritance": True,
        "app_labels": [
            "base",
            "carmel",
            "members",
            "votes",
            "contributions",
            "accounts",
        ],
    }


TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [os.path.join(BASE_DIR, "templates")],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]


WSGI_APPLICATION = "core.wsgi.application"


# Database
# https://docs.djangoproject.com/en/6.0/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}


# Password validation
# https://docs.djangoproject.com/en/6.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
        "OPTIONS": {
            "min_length": 10,
        },
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
    {
        "NAME": "core.password_validators.StrongPasswordValidator",
    },
]

# AUTHENTICATION_BACKENDS = [
#     'members.backends.EmailBackend',
# ]

# Internationalization
# https://docs.djangoproject.com/en/6.0/topics/i18n/

LANGUAGE_CODE = "pt-BR"

TIME_ZONE = "America/Sao_Paulo"

USE_I18N = True

USE_TZ = True

ROLEPERMISSIONS_MODULE = "core.roles"

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/6.0/howto/static-files/

STATIC_URL = "/static/"


STATICFILES_DIRS = [
    BASE_DIR / "static",
]

STATIC_ROOT = BASE_DIR / "staticfiles"


STATICFILES_FINDERS = [
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
    "compressor.finders.CompressorFinder",
]

# Compressor
COMPRESS_ENABLED = True
COMPRESS_OFFLINE = True


COMPRESS_PRECOMPILERS = (("text/x-scss", "django_libsass.SassCompiler"),)

if DEBUG:
    EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
