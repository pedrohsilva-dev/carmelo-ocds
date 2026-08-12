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


# Backend customizado: autentica por e-mail OU nome do membro
AUTHENTICATION_BACKENDS = [
    "members.backends.EmailBackend",
    "django.contrib.auth.backends.ModelBackend",
]


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


# URL do login usada pelo login_required/redirects de autenticação
LOGIN_URL = "/contas/entrar/"


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
                "django.template.context_processors.csrf",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]


# ==============================
# DATABASE
# ==============================


if DEBUG == False:
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
if DEBUG == True:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
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
# ADMIN (JAZZMIN) — IDENTIDADE DO SISTEMA
# ==============================

JAZZMIN_SETTINGS = {
    "site_title": "OCDS · Sistema do Carmelo",
    "site_header": "Ordem dos Carmelitas Descalços Seculares",
    "site_brand": "OCDS",
    # Logo do sistema (caminho relativo a STATIC_URL)
    "site_logo": "assets/brand_gold.png",
    "site_logo_classes": "img-circle",
    "welcome_sign": "Bem-vindo ao Sistema de Gestão do Carmelo",
    "copyright": "OCDS · Comunidade Alegria da Sagrada Face",
    "default_theme_mode": "auto",
    "search_model": ["members.Member", "carmel.Carmel"],
    "show_sidebar": True,
    "navigation_expanded": True,
    "hide_apps": [],
    "hide_models": [],
    "order_with_respect_to": ["carmel", "members", "votes", "contributions", "contacts", "accounts"],
    "custom_links": {
        "carmel": [
            {
                "name": "Ver site",
                "url": "/",
                "icon": "fas fa-globe",
            }
        ]
    },
    "icons": {
        "carmel.Carmel": "fas fa-church",
        "members.Member": "fas fa-user",
        "members.Phone": "fas fa-phone",
        "members.Address": "fas fa-map-marker-alt",
        "votes.Vote": "fas fa-vote-yea",
        "votes.VotesRegistration": "fas fa-list-check",
        "contributions.Contribution": "fas fa-hand-holding-usd",
        "accounts.ResetPasswordAccess": "fas fa-key",
        "auth.Group": "fas fa-users-cog",
    },
    "default_icon_parents": "fas fa-chevron-circle-right",
    "default_icon_children": "fas fa-circle",
    "related_modal_active": True,
    "show_ui_builder": True,
    "changeform_format": "horizontal_tabs",
    "changeform_format_overrides": {
        "auth.user": "collapsible",
        "auth.group": "vertical_tabs",
    },
}

JAZZMIN_UI_TWEAKS = {
    "navbar_small_text": False,
    "footer_small_text": False,
    "body_small_text": False,
    "brand_small_text": False,
    "brand_colour": "navbar-dark",
    "accent": "accent-warning",
    "navbar": "navbar-dark",
    "no_navbar_border": False,
    "navbar_fixed": False,
    "layout_boxed": False,
    "footer_fixed": False,
    "sidebar_fixed": False,
    "sidebar": "sidebar-dark-maroon",
    "sidebar_nav_small_text": False,
    "sidebar_disable_expand": False,
    "sidebar_nav_child_indent": False,
    "sidebar_nav_compact_style": False,
    "sidebar_nav_legacy_style": False,
    "sidebar_nav_flat_style": False,
    "theme": "darkly",
    "button_classes": {
        "primary": "btn-outline-primary",
        "secondary": "btn-outline-secondary",
        "info": "btn-outline-info",
        "warning": "btn-outline-warning",
        "danger": "btn-outline-danger",
        "success": "btn-outline-success",
    },
}


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
if DEBUG == False:
    SECURE_SSL_REDIRECT = True

    SECURE_HSTS_SECONDS = 31536000

    X_FRAME_OPTIONS = "DENY"

    CSP_DEFAULT_SRC = ("'self'",)
    CSP_SCRIPT_SRC = ("'self'",)

    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

    # Cookies de sessão/CSRF marcados como seguros (HTTPS) apenas quando a env
    # autorizar — definidos uma única vez aqui (sem sobrescrita duplicada).
    SESSION_COOKIE_SECURE = (
        os.getenv("SESSION_COOKIE_SECURE", "False").lower() == "true"
    )

    CSRF_COOKIE_SECURE = os.getenv("CSRF_COOKIE_SECURE", "False").lower() == "true"

    # ==============================
    # ORIGENS CONFIÁVEIS (CSRF)
    # ==============================
    # Evita erros 403 de permissão quando a aplicação é acessada por outras
    # origens (domínio customizado, domínio público do Railway, serviços e
    # bibliotecas externas que enviam requisições com Origin próprio).
    #
    # Fontes combinadas:
    #   1. CSRF_TRUSTED_ORIGINS (env, separada por vírgula) — origens extras;
    #   2. RAILWAY_PUBLIC_DOMAIN / RAILWAY_APP_DOMAIN — definidos automaticamente
    #      pelo Railway em produção;
    #   3. hosts concretos de ALLOWED_HOSTS (o curinga "*" é ignorado).
    def _split_origins(*sources):
        origins = []
        for source in sources:
            if not source:
                continue
            origins.extend(o.strip() for o in source.split(",") if o.strip())

        # Remove duplicados preservando a ordem
        seen = set()
        return [o for o in origins if not (o in seen or seen.add(o))]

    _railway_domains = ",".join(
        f"https://{d}"
        for d in (
            os.getenv("RAILWAY_PUBLIC_DOMAIN", ""),
            os.getenv("RAILWAY_APP_DOMAIN", ""),
        )
        if d
    )

    _host_origins = ",".join(
        f"https://{h}"
        for h in ALLOWED_HOSTS
        if h not in ("*", "localhost", "127.0.0.1", "[::1]")
    )

    CSRF_TRUSTED_ORIGINS = _split_origins(
        os.getenv("CSRF_TRUSTED_ORIGINS", ""),
        _railway_domains,
        _host_origins,
    )

    # ==============================
    # EMAIL
    # ==============================

    EMAIL_BACKEND = os.getenv(
        "EMAIL_BACKEND", "django.core.mail.backends.console.EmailBackend"
    )
