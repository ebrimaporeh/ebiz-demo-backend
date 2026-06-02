"""
Base settings shared across all environments.
"""
from pathlib import Path
from decouple import config

BASE_DIR = Path(__file__).resolve().parent.parent.parent

# ─── Security ─────────────────────────────────────────────────────────────────

SECRET_KEY = config('SECRET_KEY')
ALLOWED_HOSTS = config(
    'ALLOWED_HOSTS',
    default='localhost,127.0.0.1',
    cast=lambda v: [h.strip() for h in v.split(',')],
)

# ─── Applications ─────────────────────────────────────────────────────────────

DJANGO_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

THIRD_PARTY_APPS = [
    'rest_framework',
    'rest_framework_simplejwt',
    'rest_framework_simplejwt.token_blacklist',
    'corsheaders',
    'storages',
]

LOCAL_APPS = [
    'apps.users',
    'apps.taxonomy',
    'apps.datasets',
    'apps.pipeline',
    'apps.audit',
    'apps.catalog',
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

# ─── Middleware ────────────────────────────────────────────────────────────────

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# ─── URLs & WSGI ──────────────────────────────────────────────────────────────

ROOT_URLCONF = 'config.urls'
WSGI_APPLICATION = 'config.wsgi.application'

# ─── Templates ────────────────────────────────────────────────────────────────

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
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

# ─── Database (Supabase PostgreSQL — Transaction Pooler) ──────────────────────

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME':     config('DB_NAME',     default='postgres'),
        'USER':     config('DB_USER',     default='postgres.neeuqoqxvmpbbskrxste'),
        'PASSWORD': config('DB_PASSWORD'),
        'HOST':     config('DB_HOST',     default='aws-1-eu-central-1.pooler.supabase.com'),
        'PORT':     config('DB_PORT',     default='6543'),
        'OPTIONS': {
            'sslmode': 'require',
        },
        'CONN_MAX_AGE': 60,
    }
}

# ─── Password validation ───────────────────────────────────────────────────────

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# ─── Internationalisation ──────────────────────────────────────────────────────

LANGUAGE_CODE = 'en-us'
TIME_ZONE     = 'Africa/Banjul'
USE_I18N      = True
USE_TZ        = True

# ─── Static & Media ───────────────────────────────────────────────────────────

STATIC_URL  = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

MEDIA_URL = '/media/'

# ─── Supabase (project client) ────────────────────────────────────────────────

SUPABASE_URL              = config('SUPABASE_URL',
    default='https://neeuqoqxvmpbbskrxste.supabase.co')
SUPABASE_SERVICE_ROLE_KEY = config('SUPABASE_SERVICE_ROLE_KEY', default='')
SUPABASE_ANON_KEY         = config('SUPABASE_ANON_KEY',         default='')

# ─── Supabase Storage ─────────────────────────────────────────────────────────
# Files are uploaded via the Supabase storage client and their public URLs
# stored directly in model URLFields.  No django-storages FileField magic needed.
#
# Public URL pattern:
#   {SUPABASE_URL}/storage/v1/object/public/{bucket}/{path}

SUPABASE_BUCKET_NAME = config('SUPABASE_BUCKET_NAME', default='gambih-files')

# Bucket folder layout
STORAGE_FOLDER_AVATARS  = 'avatars'
STORAGE_FOLDER_DATASETS = 'datasets'
STORAGE_FOLDER_RAW      = 'raw'

# Also keep S3-compatible settings for django-storages (production fallback)
SUPABASE_STORAGE_KEY    = config('SUPABASE_STORAGE_KEY',    default='')
SUPABASE_STORAGE_SECRET = config('SUPABASE_STORAGE_SECRET', default='')
SUPABASE_STORAGE_S3_URL = f'{SUPABASE_URL}/storage/v1/s3'

AWS_ACCESS_KEY_ID       = SUPABASE_STORAGE_KEY
AWS_SECRET_ACCESS_KEY   = SUPABASE_STORAGE_SECRET
AWS_STORAGE_BUCKET_NAME = SUPABASE_BUCKET_NAME
AWS_S3_ENDPOINT_URL     = SUPABASE_STORAGE_S3_URL
AWS_S3_REGION_NAME      = 'eu-central-1'
AWS_DEFAULT_ACL         = 'public-read'
AWS_S3_FILE_OVERWRITE   = False
AWS_QUERYSTRING_AUTH    = False

# ─── Django REST Framework ────────────────────────────────────────────────────

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
    'DEFAULT_FILTER_BACKENDS': [
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ],
}

# ─── JWT ──────────────────────────────────────────────────────────────────────

from datetime import timedelta

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME':  timedelta(minutes=config('ACCESS_TOKEN_LIFETIME_MINUTES', default=60, cast=int)),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=config('REFRESH_TOKEN_LIFETIME_DAYS', default=7, cast=int)),
    'ROTATE_REFRESH_TOKENS':  True,
    'BLACKLIST_AFTER_ROTATION': True,
    'AUTH_HEADER_TYPES': ('Bearer',),
}

# ─── CORS ─────────────────────────────────────────────────────────────────────

CORS_ALLOWED_ORIGINS = config(
    'CORS_ALLOWED_ORIGINS',
    default='http://localhost:5173,http://127.0.0.1:5173',
    cast=lambda v: [s.strip() for s in v.split(',')],
)
CORS_ALLOW_CREDENTIALS = True

# ─── Custom User Model ────────────────────────────────────────────────────────

AUTH_USER_MODEL = 'users.User'

# ─── Default PK ───────────────────────────────────────────────────────────────

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
