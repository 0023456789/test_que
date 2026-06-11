import os
import shutil
import subprocess

BASE_DIR = r"d:\test_que\tieuluan.v01\services"

SERVICES = {
    "patient_service": {"port": 8001, "db": "patient_db"},
    "doctor_service": {"port": 8002, "db": "doctor_db"},
    "appointment_service": {"port": 8003, "db": "appointment_db"},
    "emr_service": {"port": 8004, "db": "emr_db"},
    "pharmacy_service": {"port": 8005, "db": "pharmacy_db"},
    "billing_service": {"port": 8006, "db": "billing_db"},
    "notification_service": {"port": 8007, "db": "notification_db"},
}

DOCKERFILE_TEMPLATE = """FROM python:3.11-slim
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
WORKDIR /app
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt
COPY . /app/
EXPOSE {port}
CMD ["python", "manage.py", "runserver", "0.0.0.0:{port}"]
"""

REQUIREMENTS_TEMPLATE = """django>=4.2
djangorestframework>=3.14
django-cors-headers>=4.0
psycopg2-binary>=2.9
PyJWT>=2.8
requests>=2.31
"""

SETTINGS_TEMPLATE = """import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
SECRET_KEY = 'django-insecure-test-key'
DEBUG = True
ALLOWED_HOSTS = ['*']

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'corsheaders',
    'api',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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

WSGI_APPLICATION = 'config.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
# In production, parse DATABASE_URL from os.environ
db_url = os.environ.get("DATABASE_URL")
if db_url:
    import dj_database_url
    DATABASES['default'] = dj_database_url.parse(db_url)

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True
STATIC_URL = 'static/'
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
CORS_ALLOW_ALL_ORIGINS = True

REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.AllowAny',
    ]
}
"""

URLS_TEMPLATE = """from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('api.urls')),
]
"""

API_URLS_TEMPLATE = """from django.urls import path
from rest_framework.routers import DefaultRouter

router = DefaultRouter()

urlpatterns = [
    path('', include(router.urls) if router.urls else []),
]
"""

for service_name, config in SERVICES.items():
    service_dir = os.path.join(BASE_DIR, service_name)
    os.makedirs(service_dir, exist_ok=True)
    
    # Remove FastAPI main.py if exists
    fastapi_main = os.path.join(service_dir, "main.py")
    if os.path.exists(fastapi_main):
        os.remove(fastapi_main)

    # Initialize Django Project
    # Try running django-admin startproject config . inside the folder
    if not os.path.exists(os.path.join(service_dir, "manage.py")):
        subprocess.run(["django-admin", "startproject", "config", "."], cwd=service_dir, shell=True)
        subprocess.run(["django-admin", "startapp", "api"], cwd=service_dir, shell=True)

    # Overwrite Dockerfile
    with open(os.path.join(service_dir, "Dockerfile"), "w") as f:
        f.write(DOCKERFILE_TEMPLATE.format(port=config["port"]))

    # Overwrite requirements.txt
    with open(os.path.join(service_dir, "requirements.txt"), "w") as f:
        f.write(REQUIREMENTS_TEMPLATE)

    # Overwrite config/settings.py
    settings_path = os.path.join(service_dir, "config", "settings.py")
    if os.path.exists(settings_path):
        with open(settings_path, "w") as f:
            f.write(SETTINGS_TEMPLATE)

    # Overwrite config/urls.py
    urls_path = os.path.join(service_dir, "config", "urls.py")
    if os.path.exists(urls_path):
        with open(urls_path, "w") as f:
            f.write(URLS_TEMPLATE)

    # Create api/urls.py
    api_urls_path = os.path.join(service_dir, "api", "urls.py")
    if not os.path.exists(api_urls_path):
        with open(api_urls_path, "w") as f:
            f.write(API_URLS_TEMPLATE)

print("Scaffolding complete.")
