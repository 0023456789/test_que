import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY", "dev-secret-gateway")
DEBUG = os.environ.get("DEBUG", "False") == "True"
ALLOWED_HOSTS = ["*"]

INSTALLED_APPS = [
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "corsheaders",
    "rest_framework",
    "gateway",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
    "gateway.middleware.RequestLoggingMiddleware",
]

ROOT_URLCONF = "config.urls"
WSGI_APPLICATION = "config.wsgi.application"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "gateway.db",
    }
}

# Service URLs
AUTH_SERVICE_URL       = os.environ.get("AUTH_SERVICE_URL",       "http://auth-service:8000")
CUSTOMER_SERVICE_URL   = os.environ.get("CUSTOMER_SERVICE_URL",   "http://customer-service:8000")
STAFF_SERVICE_URL      = os.environ.get("STAFF_SERVICE_URL",      "http://staff-service:8000")
MANAGER_SERVICE_URL    = os.environ.get("MANAGER_SERVICE_URL",    "http://manager-service:8000")
CATALOG_SERVICE_URL    = os.environ.get("CATALOG_SERVICE_URL",    "http://catalog-service:8000")
BOOK_SERVICE_URL       = os.environ.get("BOOK_SERVICE_URL",       "http://book-service:8000")
CART_SERVICE_URL       = os.environ.get("CART_SERVICE_URL",       "http://cart-service:8000")
ORDER_SERVICE_URL      = os.environ.get("ORDER_SERVICE_URL",      "http://order-service:8000")
SHIP_SERVICE_URL       = os.environ.get("SHIP_SERVICE_URL",       "http://ship-service:8000")
PAY_SERVICE_URL        = os.environ.get("PAY_SERVICE_URL",        "http://pay-service:8000")
COMMENT_RATE_SERVICE_URL = os.environ.get("COMMENT_RATE_SERVICE_URL", "http://comment-rate-service:8000")
RECOMMENDER_SERVICE_URL  = os.environ.get("RECOMMENDER_SERVICE_URL",  "http://recommender-ai-service:8000")

JWT_SECRET_KEY       = os.environ.get("JWT_SECRET_KEY", "super-secret-jwt-key")
REDIS_URL            = os.environ.get("REDIS_URL", "redis://redis:6379/0")
RATE_LIMIT_PER_MINUTE = int(os.environ.get("RATE_LIMIT_PER_MINUTE", "60"))

CORS_ALLOW_ALL_ORIGINS = True
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_TZ = True
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "gateway": {
            "format": "[GATEWAY] {levelname} {asctime} {message}",
            "style": "{",
        }
    },
    "handlers": {"console": {"class": "logging.StreamHandler", "formatter": "gateway"}},
    "root": {"handlers": ["console"], "level": "INFO"},
}
