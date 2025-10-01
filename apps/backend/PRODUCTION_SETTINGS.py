"""
V1 Production Settings Checklist

This file documents the key settings that need to be configured for production deployment.
Copy these settings to your production settings file and adjust values as needed.
"""

# Security Settings - REQUIRED for production
DEBUG = False
ALLOWED_HOSTS = ["your-domain.com", "www.your-domain.com"]

# SSL/HTTPS Settings
SECURE_SSL_REDIRECT = True
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SECURE_HSTS_SECONDS = 31536000  # 1 year
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True
X_FRAME_OPTIONS = "DENY"

# Session and Cookie Security
SESSION_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = "Strict"
CSRF_COOKIE_SECURE = True
CSRF_COOKIE_HTTPONLY = True
CSRF_COOKIE_SAMESITE = "Strict"

# Content Security Policy
CSP_ENABLED = True
CSP_DEFAULT_SRC = "'self'"
CSP_SCRIPT_SRC = "'self'"  # Remove 'unsafe-eval' for production
CSP_STYLE_SRC = "'self' 'unsafe-inline'"  # Keep for Tailwind
CSP_IMG_SRC = "'self' data: https:"
CSP_FONT_SRC = "'self'"
CSP_CONNECT_SRC = "'self'"
CSP_FRAME_SRC = "'none'"
CSP_OBJECT_SRC = "'none'"
CSP_BASE_URI = "'self'"
# CSP_REPORT_URI = '/csp-report/'  # Optional: set up CSP reporting

# Cache Configuration - REQUIRED for performance
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.redis.RedisCache",
        "LOCATION": "redis://127.0.0.1:6379/1",
        "OPTIONS": {
            "CONNECTION_POOL_KWARGS": {
                "max_connections": 20,
                "retry_on_timeout": True,
            }
        },
        "KEY_PREFIX": "mysite",
        "TIMEOUT": 900,  # 15 minutes default
    }
}

# Database Configuration - Optimize for production
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": "mysite_production",
        "USER": "mysite_user",
        "PASSWORD": "your-secure-password",
        "HOST": "localhost",
        "PORT": "5432",
        "OPTIONS": {
            "conn_max_age": 600,  # Connection pooling
            "OPTIONS": {
                "MAX_CONNS": 20,
                "MIN_CONNS": 5,
            },
        },
    }
}

# Static Files - Configure for CDN
STATIC_URL = "/static/"
STATIC_ROOT = "/var/www/mysite/static/"
STATICFILES_STORAGE = "django.contrib.staticfiles.storage.ManifestStaticFilesStorage"

# Media Files
MEDIA_URL = "/media/"
MEDIA_ROOT = "/var/www/mysite/media/"

# Email Configuration
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = "smtp.your-provider.com"
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = "your-email@domain.com"
EMAIL_HOST_PASSWORD = "your-email-password"
DEFAULT_FROM_EMAIL = "noreply@your-domain.com"
SERVER_EMAIL = "admin@your-domain.com"

# Logging Configuration
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "{levelname} {asctime} {module} {process:d} {thread:d} {message}",
            "style": "{",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "verbose",
        },
        "file": {
            "class": "logging.FileHandler",
            "filename": "/var/log/mysite/django.log",
            "formatter": "verbose",
        },
    },
    "root": {
        "handlers": ["console", "file"],
        "level": "INFO",
    },
    "loggers": {
        "django": {
            "handlers": ["console", "file"],
            "level": "INFO",
            "propagate": False,
        },
        "apps.core": {
            "handlers": ["console", "file"],
            "level": "INFO",
            "propagate": False,
        },
    },
}

# Error Reporting - Configure Sentry or similar
# SENTRY_DSN = 'https://your-sentry-dsn'

# Performance Settings
USE_TZ = True
USE_I18N = True
USE_L10N = True

# Admin Security
ADMIN_URL = "admin-secure-path-here/"  # Change from default 'admin/'

# Context Processors - Ensure all are included
TEMPLATES[0]["OPTIONS"]["context_processors"].extend([
    "apps.core.context_processors.site_config",
    "apps.core.context_processors.security",
    "apps.core.context_processors.vite",
])

# Middleware - Ensure CSP and security middleware are included
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "apps.core.middleware.csp.CSPNonceMiddleware",  # Add CSP middleware
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "apps.core.middleware.feature_flags.FeatureFlagMiddleware",  # Add feature flags
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]
