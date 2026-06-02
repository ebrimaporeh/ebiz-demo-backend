"""
Production settings — DEBUG off, Supabase S3 storage, strict security.
"""
from .base import *  # noqa: F401, F403

DEBUG = False

# Use Supabase S3-compatible storage for all uploaded files
DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'

# HTTPS
SECURE_SSL_REDIRECT         = True
SECURE_HSTS_SECONDS         = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD         = True
SESSION_COOKIE_SECURE       = True
CSRF_COOKIE_SECURE          = True

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'WARNING',
    },
}
