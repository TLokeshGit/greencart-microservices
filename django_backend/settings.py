from pathlib import Path
import os
from dotenv import load_dotenv
from datetime import timedelta
import dj_database_url
from corsheaders.defaults import default_headers

# Load .env only in development
if os.getenv("RENDER") != "true":
    load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

# === Security ===
SECRET_KEY = os.getenv("SECRET_KEY", "fallback-secret-key")
DEBUG = os.getenv("DEBUG", "True").lower() == "true"

raw_hosts = os.getenv("ALLOWED_HOSTS")
ALLOWED_HOSTS = (
    [h.strip() for h in raw_hosts.split(",") if h.strip()]
    if raw_hosts else ["127.0.0.1", "localhost"]
)

# === Stripe ===
STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY", "")
STRIPE_PUBLISHABLE_KEY = os.getenv("STRIPE_PUBLISHABLE_KEY", "")
STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET", "")

# === Database ===
DATABASES = {
    "default": dj_database_url.config(default="sqlite:///" + str(BASE_DIR / "db.sqlite3"))
}

# === Installed Apps ===
INSTALLED_APPS = [
    "jazzmin",
    "corsheaders",
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
    "shop"
]

# === Middleware ===
MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

# === URL + WSGI ===
ROOT_URLCONF = "django_backend.urls"
WSGI_APPLICATION = "django_backend.wsgi.application"

# === Templates ===
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "shop" / "templates", BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "django.template.context_processors.media",
            ],
        },
    },
]

# === Static + Media ===
STATIC_URL = "/static/"
STATICFILES_DIRS = [
    BASE_DIR / "shop" / "static",
    # BASE_DIR / "static",  # ✅ remove or comment this
]
STATIC_ROOT = BASE_DIR / "staticfiles"
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

# === AWS S3 ===
if not DEBUG:
    DEFAULT_FILE_STORAGE = "storages.backends.s3boto3.S3Boto3Storage"
    AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
    AWS_STORAGE_BUCKET_NAME = os.getenv("AWS_STORAGE_BUCKET_NAME")
    AWS_S3_REGION_NAME = os.getenv("AWS_S3_REGION_NAME", "us-east-1")
    AWS_S3_CUSTOM_DOMAIN = f"{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com"
    MEDIA_URL = f"https://{AWS_S3_CUSTOM_DOMAIN}/"

# === CORS ===
CORS_ALLOW_ALL_ORIGINS = DEBUG
if not DEBUG:
    raw_origins = os.getenv("CORS_ALLOWED_ORIGINS", "")
    CORS_ALLOWED_ORIGINS = [o.strip() for o in raw_origins.split(",") if o.startswith("http")]
else:
    CORS_ALLOWED_ORIGINS = ["http://localhost:3000", "http://127.0.0.1:3000"]

CORS_ALLOW_HEADERS = list(default_headers) + ["authorization"]
CORS_ALLOW_CREDENTIALS = True

# === Authentication ===
AUTH_USER_MODEL = "shop.Customer"

REST_FRAMEWORK = {
    "DEFAULT_PERMISSION_CLASSES": ["rest_framework.permissions.IsAuthenticated"],
    "DEFAULT_AUTHENTICATION_CLASSES": ["rest_framework_simplejwt.authentication.JWTAuthentication"],
    "DEFAULT_SCHEMA_CLASS": "rest_framework.schemas.coreapi.AutoSchema",
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

# === Email ===
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = os.getenv("EMAIL_HOST", "smtp.example.com")
EMAIL_PORT = int(os.getenv("EMAIL_PORT", 587))
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER", "")
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD", "")

# === Logging ===
logs_path = BASE_DIR / "logs"
logs_path.mkdir(parents=True, exist_ok=True)

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {"format": "{levelname} {asctime} {module} {message}", "style": "{"},
        "simple": {"format": "{levelname} {message}", "style": "{"},
    },
    "handlers": {
        "console": {"class": "logging.StreamHandler", "formatter": "verbose"},
        "file": {
            "class": "logging.FileHandler",
            "filename": BASE_DIR / "logs/debug.log",
            "formatter": "verbose",
        },
    },
    "loggers": {
        "django": {"handlers": ["console", "file"], "level": "INFO"},
        "shop": {"handlers": ["console", "file"], "level": "DEBUG"},
        "rest_framework": {"handlers": ["console", "file"], "level": "DEBUG"},
    },
}

# === Swagger ===
SWAGGER_SETTINGS = {
    "SECURITY_DEFINITIONS": {
        "Bearer": {
            "type": "apiKey",
            "name": "Authorization",
            "in": "header"
        }
    },
    "USE_SESSION_AUTH": True,
    "VALIDATOR_URL": None,
    "JSON_EDITOR": True,
    "SECURITY_REQUIREMENTS": [{"Bearer": []}],
}

# === Admin Branding ===
JAZZMIN_SETTINGS = {
    "site_logo": "admin/img/logo.png",
    "site_icon": "admin/img/favicon.ico",
    "site_title": "GreenCart Admin",
    "site_header": "GreenCart Administration",
    "site_brand": "GreenCart",
    "welcome_sign": "Welcome to GreenCart Admin",
}

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
AUTHENTICATION_BACKENDS = ["django.contrib.auth.backends.ModelBackend"]
