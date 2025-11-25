"""
Django settings for vote_x_backend project.
"""

from pathlib import Path
import os
import sys

import dj_database_url
from dotenv import load_dotenv

# -------------------------------------------------------------------
# Base paths / env
# -------------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent

# Load .env for local development (Render uses real env vars)
load_dotenv(BASE_DIR / ".env")

# -------------------------------------------------------------------
# Core settings
# -------------------------------------------------------------------
# Use env in production, fallback dev key only if missing
SECRET_KEY = os.getenv(
    "SECRET_KEY",
    "django-insecure-dev-only-change-me"
)

DEBUG = os.getenv("DEBUG", "False") == "True"

# Example env for production:
# ALLOWED_HOSTS=your-backend.onrender.com,localhost,127.0.0.1
ALLOWED_HOSTS = os.getenv(
    "ALLOWED_HOSTS",
    "localhost,127.0.0.1"
).split(",")

# Optional: frontend URL, e.g. https://your-frontend.vercel.app
FRONTEND_URL = os.getenv("FRONTEND_URL")  # set this in Render later

# Testing flag
TESTING = "test" in sys.argv

# -------------------------------------------------------------------
# Application definition
# -------------------------------------------------------------------
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    # Third-party apps
    "corsheaders",
    "rest_framework",
    "rest_framework.authtoken",
    "drf_yasg",

    # Local apps
    "users",
    "polls",
    "votes",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    # Whitenoise for static files in production
    "whitenoise.middleware.WhiteNoiseMiddleware",
    # CORS
    "corsheaders.middleware.CorsMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "vote_x_backend.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "vote_x_backend.wsgi.application"

# -------------------------------------------------------------------
# Database (Neon via DATABASE_URL)
# -------------------------------------------------------------------
# Neon / PostgreSQL requires channel binding tweak for some psycopg builds
os.environ["PGCHANNELBINDING"] = "disable"

DATABASES = {
    "default": dj_database_url.parse(
        os.environ.get("DATABASE_URL"),
        conn_max_age=600,
        ssl_require=True,
    )
}

# Local tests (python manage.py test) – use in-memory SQLite for speed
if TESTING and not os.environ.get("GITHUB_WORKFLOW"):
    print("⚙️ Using SQLite for local test environment")
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": ":memory:",
        }
    }

# CI tests (GitHub Actions)
if os.environ.get("GITHUB_WORKFLOW"):
    print("⚙️ Using SQLite for GitHub Actions CI tests")
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": ":memory:",
        }
    }

# -------------------------------------------------------------------
# Password validation
# -------------------------------------------------------------------
AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

# -------------------------------------------------------------------
# Internationalization
# -------------------------------------------------------------------
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

# -------------------------------------------------------------------
# Static files (Whitenoise + Render)
# -------------------------------------------------------------------
STATIC_URL = "/static/"
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_DIRS = []
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"
WHITENOISE_USE_FINDERS = True


# Whitenoise storage
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

# -------------------------------------------------------------------
# Custom User model
# -------------------------------------------------------------------
AUTH_USER_MODEL = "users.User"

# -------------------------------------------------------------------
# REST Framework / JWT / Throttling
# -------------------------------------------------------------------
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": (
        "rest_framework.permissions.IsAuthenticated",
    ),
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 10,
    "EXCEPTION_HANDLER": "core.exceptions.custom_exception_handler",

    # Throttling
    "DEFAULT_THROTTLE_CLASSES": [
        "rest_framework.throttling.AnonRateThrottle",
        "rest_framework.throttling.UserRateThrottle",
    ],
    "DEFAULT_THROTTLE_RATES": {
        "anon": "100/day",
        "user": "1000/day",
    },
}

from datetime import timedelta

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=60),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
    "AUTH_HEADER_TYPES": ("Bearer",),
}

SWAGGER_SETTINGS = {
    "USE_SESSION_AUTH": False,
    "SECURITY_DEFINITIONS": {
        "Bearer": {
            "type": "apiKey",
            "name": "Authorization",
            "in": "header",
            "description": "JWT Authorization header. Example: Bearer <token>",
        }
    },
}

AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
]

# -------------------------------------------------------------------
# CORS / CSRF (Frontend ↔ Backend)
# -------------------------------------------------------------------
# DEV: allow all origins for local dev
if DEBUG:
    CORS_ALLOW_ALL_ORIGINS = True
else:
    CORS_ALLOW_ALL_ORIGINS = False

# Allow specific origins (dev + production frontend)
CORS_ALLOWED_ORIGINS = [
    "http://localhost:5173",
    "http://localhost:3000",
    "http://127.0.0.1:5173",
] + ([FRONTEND_URL] if FRONTEND_URL else [])

CORS_ALLOW_CREDENTIALS = True

CORS_ALLOW_HEADERS = [
    "accept",
    "accept-encoding",
    "authorization",
    "content-type",
    "dnt",
    "origin",
    "user-agent",
    "x-csrftoken",
    "x-requested-with",
]

# CSRF (only relevant if you ever use cookies / forms)
CSRF_TRUSTED_ORIGINS = [
    "https://vote-x-backend.onrender.com",
]

if FRONTEND_URL:
    # Ensure https://your-frontend.vercel.app works for CSRF if you ever use cookies
    CSRF_TRUSTED_ORIGINS.append(FRONTEND_URL)

# -------------------------------------------------------------------
# Default primary key field type
# -------------------------------------------------------------------
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# LOAD STATIC SWAGGER UI FROM CDN
STATIC_SWAGGER_UI_DIST_URL = "https://cdnjs.cloudflare.com/ajax/libs/swagger-ui/4.15.5/"
