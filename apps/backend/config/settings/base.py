"""Django settings for config project.

Base configuration using typed environment settings via Pydantic.
Environment-specific overrides are in dev.py, prod.py, staging.py, test.py.
"""

from pathlib import Path

from .env import get_settings

# -----------------------------------------------------------------------------
# Environment Configuration (typed, validated via Pydantic)
# -----------------------------------------------------------------------------
env = get_settings()

# -----------------------------------------------------------------------------
# Path Configuration
# -----------------------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent.parent  # apps/backend
REPO_ROOT = BASE_DIR.parents[1]

# -----------------------------------------------------------------------------
# Core Django Settings
# -----------------------------------------------------------------------------
DEBUG = env.DEBUG
SECRET_KEY = env.SECRET_KEY.get_secret_value()
ALLOWED_HOSTS = env.ALLOWED_HOSTS
ROOT_URLCONF = "config.urls"
WSGI_APPLICATION = "config.wsgi.application"
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# -----------------------------------------------------------------------------
# Applications
# -----------------------------------------------------------------------------
INSTALLED_APPS = [
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "apps.core",
    "apps.pages",
    "apps.contact",  # Our contact form app
    "apps.blog",  # Blog functionality
    "apps.projects",  # Portfolio/projects
]

# Conditionally add admin based on feature flag
if env.ENABLE_ADMIN:
    INSTALLED_APPS.insert(0, "django.contrib.admin")

# Conditionally add compressor if enabled
if env.ENABLE_COMPRESSION:
    INSTALLED_APPS.append("compressor")

# -----------------------------------------------------------------------------
# Middleware
# -----------------------------------------------------------------------------
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "apps.core.middleware.request_id.RequestIDMiddleware",  # Request ID tracking
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "apps.core.middleware.csp_nonce.CSPNonceMiddleware",
]

# -----------------------------------------------------------------------------
# Templates
# -----------------------------------------------------------------------------
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.template.context_processors.i18n",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "apps.core.context_processors.vite",
                "apps.core.context_processors.site_context",
                "apps.core.context_processors.security",
            ],
        },
    },
]

# -----------------------------------------------------------------------------
# Database Configuration
# -----------------------------------------------------------------------------
if env.DATABASE_URL:
    # Use DATABASE_URL if provided (e.g., PostgreSQL in production)
    try:
        import dj_database_url  # type: ignore[import]

        DATABASES = {"default": dj_database_url.parse(env.DATABASE_URL)}
    except ImportError as e:
        raise ImportError(
            "dj-database-url is required when DATABASE_URL is set. "
            "Install it with: pip install dj-database-url"
        ) from e
else:
    # Default to SQLite
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": (BASE_DIR / env.SQLITE_PATH).resolve(),
        }
    }

# -----------------------------------------------------------------------------
# Internationalization
# -----------------------------------------------------------------------------
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True


# -----------------------------------------------------------------------------
# Static Files & Media
# -----------------------------------------------------------------------------
STATIC_URL = env.STATIC_URL
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [
    BASE_DIR / "static",
    BASE_DIR / "static" / "dist",
]
MEDIA_URL = env.MEDIA_URL
MEDIA_ROOT = BASE_DIR / "media"

# Static files finders (with compressor support)
STATICFILES_FINDERS = [
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
]
if env.ENABLE_COMPRESSION:
    STATICFILES_FINDERS.append("compressor.finders.CompressorFinder")


# -----------------------------------------------------------------------------
# Vite Integration
# -----------------------------------------------------------------------------
VITE_DEV = env.VITE_DEV if env.VITE_DEV is not None else DEBUG
VITE_DEV_SERVER_URL = env.VITE_DEV_SERVER_URL
VITE_MANIFEST_PATH = str(
    env.VITE_MANIFEST_PATH or (BASE_DIR / "static" / "dist" / "manifest.json")
)


# -----------------------------------------------------------------------------
# Security Configuration
# -----------------------------------------------------------------------------
SESSION_COOKIE_SECURE = env.SESSION_COOKIE_SECURE
CSRF_COOKIE_SECURE = env.CSRF_COOKIE_SECURE
SECURE_SSL_REDIRECT = env.SECURE_SSL_REDIRECT
SECURE_HSTS_SECONDS = env.SECURE_HSTS_SECONDS
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True
REFERRER_POLICY = "strict-origin-when-cross-origin"
CSP_NONCE_ENABLED = env.CSP_NONCE_ENABLED

# -----------------------------------------------------------------------------
# Cache Configuration
# -----------------------------------------------------------------------------
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "default",
        "TIMEOUT": env.CACHE_TIMEOUT,
    }
}

# -----------------------------------------------------------------------------
# Email Configuration
# -----------------------------------------------------------------------------
EMAIL_BACKEND = env.EMAIL_BACKEND
EMAIL_HOST = env.EMAIL_HOST
EMAIL_PORT = env.EMAIL_PORT
EMAIL_HOST_USER = env.EMAIL_HOST_USER
EMAIL_HOST_PASSWORD = (
    env.EMAIL_HOST_PASSWORD.get_secret_value() if env.EMAIL_HOST_PASSWORD else ""
)
EMAIL_USE_TLS = env.EMAIL_USE_TLS
EMAIL_USE_SSL = env.EMAIL_USE_SSL
DEFAULT_FROM_EMAIL = env.DEFAULT_FROM_EMAIL

# -----------------------------------------------------------------------------
# Password Validation
# -----------------------------------------------------------------------------
AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": (
            "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"
        )
    },
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# -----------------------------------------------------------------------------
# Django Compressor (if enabled)
# -----------------------------------------------------------------------------
if env.ENABLE_COMPRESSION:
    COMPRESS_ENABLED = not DEBUG
    COMPRESS_OFFLINE = True
    COMPRESS_CSS_HASHING_METHOD = "content"
    COMPRESS_JS_HASHING_METHOD = "content"


# -----------------------------------------------------------------------------
# Logging Configuration
# -----------------------------------------------------------------------------
if env.LOG_FILE_PATH:
    # Auto-create parent directories for log file
    env.LOG_FILE_PATH.parent.mkdir(parents=True, exist_ok=True)
    LOGGING = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "verbose": {
                "format": (
                    "[{request_id}] {levelname} {asctime} {module} {process:d} "
                    "{thread:d} {message}"
                ),
                "style": "{",
                "()": "apps.core.logging.RequestIDFormatter",
            },
            "simple": {
                "format": "[{request_id}] {levelname} {message}",
                "style": "{",
                "()": "apps.core.logging.RequestIDFormatter",
            },
        },
        "filters": {
            "request_id": {
                "()": "apps.core.logging.RequestIDFilter",
            },
        },
        "handlers": {
            "file": {
                "class": "logging.FileHandler",
                "filename": str(env.LOG_FILE_PATH),
                "formatter": "verbose",
                "filters": ["request_id"],
            },
            "console": {
                "class": "logging.StreamHandler",
                "formatter": "simple",
                "filters": ["request_id"],
            },
        },
        "root": {
            "level": env.LOG_LEVEL,
            "handlers": ["file", "console"],
        },
    }
else:
    # Console-only logging when no file path specified
    LOGGING = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "simple": {
                "format": "[{request_id}] {levelname} {message}",
                "style": "{",
                "()": "apps.core.logging.RequestIDFormatter",
            },
        },
        "filters": {
            "request_id": {
                "()": "apps.core.logging.RequestIDFilter",
            },
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "formatter": "simple",
                "filters": ["request_id"],
            },
        },
        "root": {
            "level": env.LOG_LEVEL,
            "handlers": ["console"],
        },
    }
