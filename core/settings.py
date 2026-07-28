from pathlib import Path
import os
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent


load_dotenv(BASE_DIR / ".env")


# ==============================
# BASIC CONFIG
# ==============================

SECRET_KEY = os.getenv("SECRET_KEY")

DEBUG = os.getenv("DEBUG", "False").lower() == "true"


ALLOWED_HOSTS = ["*"]


DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


# ==============================
# APPS
# ==============================

INSTALLED_APPS = [
    "jazzmin",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # Third party
    "rolepermissions",
    # "django_extensions",
    # Local apps
    "base",
    "carmel",
    "members",
    "votes",
    "contributions",
    "accounts",
    "contacts",
]


AUTH_USER_MODEL = "members.Member"


# ==============================
# MIDDLEWARE
# ==============================

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "base.middlewares.PrefetchUserPermissionsMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "base.middlewares.HtmxMessagesMiddleware",
]


# ==============================
# URL
# ==============================

ROOT_URLCONF = "core.urls"

WSGI_APPLICATION = "core.wsgi.application"


LOGIN_REDIRECT_URL = os.getenv("LOGIN_REDIRECT_URL", "/")


# ==============================
# TEMPLATES
# ==============================

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
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


# ==============================
# DATABASE
# ==============================


DATABASES = {
    "default": {
        "ENGINE": os.getenv("DB_ENGINE", "django.db.backends.sqlite3"),
        "NAME": os.getenv("DB_NAME"),
        "USER": os.getenv("DB_USER"),
        "PASSWORD": os.getenv("DB_PASSWORD"),
        "HOST": os.getenv("DB_HOST"),
        "PORT": os.getenv("DB_PORT"),
        "CONN_MAX_AGE": int(os.getenv("DB_TIME_CONNECTION", 60)),
    }
}


# ==============================
# PASSWORD VALIDATION
# ==============================

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


# ==============================
# LANGUAGE
# ==============================

LANGUAGE_CODE = os.getenv("LANGUAGE_CODE", "pt-BR")


TIME_ZONE = os.getenv("TIME_ZONE", "America/Sao_Paulo")


USE_I18N = os.getenv("USE_I18N", "True").lower() == "true"


USE_TZ = os.getenv("USE_TZ", "True").lower() == "true"


# ==============================
# ROLES
# ==============================

ROLEPERMISSIONS_MODULE = "core.roles"


# ==============================
# STATIC FILES
# ==============================

STATIC_URL = "/static/"


STATICFILES_DIRS = [BASE_DIR / "static"]


STATIC_ROOT = BASE_DIR / "staticfiles"


STATICFILES_FINDERS = [
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
]


STORAGES = {
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedStaticFilesStorage",
    }
}

# ==============================
# SECURITY PRODUCTION
# ==============================

SECURE_SSL_REDIRECT = True

SESSION_COOKIE_SECURE = True

CSRF_COOKIE_SECURE = True

SECURE_HSTS_SECONDS = 31536000

X_FRAME_OPTIONS = "DENY"

CSP_DEFAULT_SRC = ("'self'",)
CSP_SCRIPT_SRC = ("'self'",)

SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

CSRF_TRUSTED_ORIGINS = [
    origin.strip()
    for origin in os.getenv("CSRF_TRUSTED_ORIGINS", "").split(",")
    if origin.strip()
]


SESSION_COOKIE_SECURE = os.getenv("SESSION_COOKIE_SECURE", "False").lower() == "true"


CSRF_COOKIE_SECURE = os.getenv("CSRF_COOKIE_SECURE", "False").lower() == "true"


# ==============================
# EMAIL
# ==============================

EMAIL_BACKEND = os.getenv(
    "EMAIL_BACKEND", "django.core.mail.backends.console.EmailBackend"
)
