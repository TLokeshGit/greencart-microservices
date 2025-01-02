from pathlib import Path
import os
from dotenv import load_dotenv
from datetime import timedelta
import socket
from django.contrib import admin
from corsheaders.defaults import default_headers

# Load environment variables from .env file
load_dotenv()

# Correct BASE_DIR to point to the project root
BASE_DIR = Path(__file__).resolve().parent.parent  # Changed from parent.parent.parent

# Security
SECRET_KEY = os.getenv("SECRET_KEY", "your-django-secret-key")
DEBUG = os.getenv("DEBUG", "True").lower() == "true"
ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS", "").split(",")

# Stripe API Key
STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY", "your-stripe-secret-key")

# URL Configuration
ROOT_URLCONF = "django_backend.urls"
WSGI_APPLICATION = "django_backend.wsgi.application"

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('DB_NAME', 'greencart'),
        'USER': os.getenv('DB_USER', 'postgres'),
        'PASSWORD': os.getenv('DB_PASSWORD', '1234'),
        'HOST': os.getenv('DB_HOST', 'localhost'),
        'PORT': os.getenv('DB_PORT', '5432'),
    }
}

# CORS Settings
CORS_ALLOW_ALL_ORIGINS = DEBUG  # Allow all origins only in development

# Load CORS_ALLOWED_ORIGINS from the .env file if not in DEBUG mode
CORS_ALLOWED_ORIGINS = os.getenv("CORS_ALLOWED_ORIGINS", "").split(",") if not DEBUG else [
    "http://localhost:3000",  # Example client URL; replace with your actual client URL
    # Add other allowed origins as needed
]

# Ensure CORS_ALLOWED_ORIGINS contains valid URLs
CORS_ALLOWED_ORIGINS = [
    origin.strip() for origin in CORS_ALLOWED_ORIGINS 
    if origin.startswith("http://") or origin.startswith("https://")
]

CORS_ALLOW_HEADERS = list(default_headers) + [
    'authorization',
]

# Add the following line to enable CORS credentials
CORS_ALLOW_CREDENTIALS = True

# Static and Media Files
STATIC_URL = "/static/"
STATICFILES_DIRS = [
    BASE_DIR / "shop" / "static",  # Ensure this path is correct
    BASE_DIR / "static",  # Ensure this directory exists
]
STATIC_ROOT = BASE_DIR / "staticfiles"
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

# Use Django Storages for production
if not DEBUG:
    DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
    AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
    AWS_STORAGE_BUCKET_NAME = os.getenv('AWS_STORAGE_BUCKET_NAME')
    AWS_S3_REGION_NAME = os.getenv('AWS_S3_REGION_NAME', 'us-east-1')
    AWS_S3_CUSTOM_DOMAIN = f'{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com'
    MEDIA_URL = f'https://{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com/'

# Templates
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [
            BASE_DIR / "shop" / "templates",  # Ensure this path is correct
            BASE_DIR / "templates"
        ],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "django.template.context_processors.media",  # Add this line
            ],
        },
    },
]

# Authentication
REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        # 'rest_framework.authentication.SessionAuthentication',  # Removed SessionAuthentication
    ],
    'DEFAULT_SCHEMA_CLASS': 'rest_framework.schemas.coreapi.AutoSchema',
}

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=30),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
    "AUTH_HEADER_TYPES": ("Bearer",),
    "AUTH_TOKEN_CLASSES": ("rest_framework_simplejwt.tokens.AccessToken",),
    "TOKEN_TYPE_CLAIM": "token_type",
    "BLACKLIST_AFTER_ROTATION": True,
    "ROTATE_REFRESH_TOKENS": True,
}

# Middleware
MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",  # Must be placed at the top
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

# Installed Apps
INSTALLED_APPS = [
    'jazzmin',  # Admin customization
    'corsheaders',  # CORS handling
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "rest_framework_simplejwt",
    "rest_framework_simplejwt.token_blacklist",
    "drf_yasg",
    "storages",
    "shop",  # Ensure 'shop' app is included
]

AUTH_USER_MODEL = "shop.Customer"

# Admin Site Customization
JAZZMIN_SETTINGS = {
    "site_logo": "admin/img/logo.png",
    "site_icon": "admin/img/favicon.ico",
    "site_title": "GreenCart Admin",
    "site_header": "GreenCart Administration",
    "site_brand": "GreenCart",
    "welcome_sign": "Welcome to GreenCart Admin",
}

# Security settings for production
if not DEBUG:
    SECURE_SSL_REDIRECT = True
    CSRF_COOKIE_SECURE = True
    SESSION_COOKIE_SECURE = True
    SECURE_HSTS_SECONDS = 31536000  # 1 year
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    SECURE_REFERRER_POLICY = "strict-origin-when-cross-origin"
else:
    SECURE_SSL_REDIRECT = False
    CSRF_COOKIE_SECURE = False
    SESSION_COOKIE_SECURE = False
    SECURE_HSTS_SECONDS = 0
    SECURE_HSTS_INCLUDE_SUBDOMAINS = False
    SECURE_HSTS_PRELOAD = False
    SECURE_REFERRER_POLICY = None

# CORS configuration

# Remove FORCE_SCRIPT_NAME to avoid conflicts
# FORCE_SCRIPT_NAME = '/api'

# Adjust SITE_URL to avoid conflicts
SITE_URL = os.getenv("SITE_URL", "http://localhost:8000/")  # Updated to remove '/api/'

# Ensure the 'logs' directory exists
logs_path = BASE_DIR / 'logs'
logs_path.mkdir(parents=True, exist_ok=True)

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
        'file': {
            'class': 'logging.FileHandler',
            'filename': BASE_DIR / 'logs/debug.log',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': True,
        },
        'shop': {  # Your app name
            'handlers': ['console', 'file'],
            'level': 'DEBUG',
            'propagate': False,
        },
        # Add the following logger for DRF
        'rest_framework': {
            'handlers': ['console', 'file'],
            'level': 'DEBUG',
            'propagate': False,
        },
    },
}

SWAGGER_SETTINGS = {
    'SECURITY_DEFINITIONS': {
        'Bearer': {
            'type': 'apiKey',
            'name': 'Authorization',
            'in': 'header'
        }
    },
    'USE_SESSION_AUTH': True,  # Enable session authentication
    'VALIDATOR_URL': None,
    'JSON_EDITOR': True,
    'SECURITY_REQUIREMENTS': [
        {"Bearer": []},
    ],
    # Remove 'swagger_ui_settings' as it's not supported by drf_yasg
    # 'swagger_ui_settings': {
    #     'persistAuthorization': True,
    # },
    # ...existing code...
}

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ...existing code...

AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',  # Default authentication backend
    # 'shop.backends.EmailBackend',  # Uncomment if using a custom email backend
]

# Email settings for sending password reset emails
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = os.getenv('EMAIL_HOST', 'smtp.example.com')
EMAIL_PORT = os.getenv('EMAIL_PORT', 587)
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER', 'your-email@example.com')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD', 'your-email-password')

# Stripe Configuration
STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY", "your-stripe-secret-key")
STRIPE_PUBLISHABLE_KEY = os.getenv("STRIPE_PUBLISHABLE_KEY", "your-stripe-publishable-key")
STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET", "your-stripe-webhook-secret")

# Remove any duplicated or misplaced code blocks
# Ensure the file ends properly without any class or function definitions