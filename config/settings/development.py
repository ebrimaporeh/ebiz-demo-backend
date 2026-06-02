"""
Development settings — DEBUG on, local file storage, verbose logging.
"""
from .base import *  # noqa: F401, F403

DEBUG = True

# Use local filesystem for media in development
DEFAULT_FILE_STORAGE = 'django.core.files.storage.FileSystemStorage'
MEDIA_ROOT = BASE_DIR / 'media'  # noqa: F405

# Relax CORS in dev
CORS_ALLOW_ALL_ORIGINS = True

# Django Debug Toolbar (optional — install separately)
# INSTALLED_APPS += ['debug_toolbar']
# MIDDLEWARE.insert(0, 'debug_toolbar.middleware.DebugToolbarMiddleware')
# INTERNAL_IPS = ['127.0.0.1']

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {'class': 'logging.StreamHandler'},
    },
    'root': {
        'handlers': ['console'],
        'level': 'DEBUG',
    },
    'loggers': {
        'django.db.backends': {
            'handlers': ['console'],
            'level': 'INFO',  # set to DEBUG to log all SQL queries
            'propagate': False,
        },
    },
}
