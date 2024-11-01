from pathlib import Path
from datetime import timedelta
import dj_database_url
from decouple import config
import os

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config("SECRET_KEY")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "ninja_jwt",
    "corsheaders",
    "social_django",
    "django_q",
    # installed apps
    "users",
    "posts",
]

SITE_ID = 1

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "social_media.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "social_django.context_processors.backends",
                "social_django.context_processors.login_redirect",
            ],
        },
    },
]

WSGI_APPLICATION = "social_media.wsgi.application"


# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases

DATABASES = {"default": dj_database_url.config(default=config("DATABASE_URL"))}


# Password validation
# https://docs.djangoproject.com/en/5.1/ref/settings/#auth-password-validators

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


# Internationalization
# https://docs.djangoproject.com/en/5.1/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.1/howto/static-files/

# Static files (CSS, JavaScript, Images)
STATIC_URL = "/static/"  # URL to access static files
STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")  # Directory to collect static files

# Media files (Uploaded files)
MEDIA_URL = "/media/"
MEDIA_ROOT = os.path.join(BASE_DIR, "media")

# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


NINJA_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=300),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
    # Other JWT settings as required
}


EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = config("SMTP_HOST")
EMAIL_PORT = config("SMTP_PORT")
EMAIL_USE_TLS = True
EMAIL_HOST_USER = config("SMTP_USERNAME")
EMAIL_HOST_PASSWORD = config("SMTP_PASSWORD")


AUTHENTICATION_BACKENDS = (
    "social_core.backends.twitter.TwitterOAuth",
    "social_core.backends.facebook.FacebookOAuth2",
    "social_core.backends.instagram.InstagramOAuth2",
    "social_core.backends.linkedin.LinkedinOAuth2",
    "django.contrib.auth.backends.ModelBackend",
)


SOCIAL_AUTH_JSONFIELD_ENABLED = True

# Facebook & Instagram OAuth
SOCIAL_AUTH_FACEBOOK_KEY = "your-facebook-client-id"
SOCIAL_AUTH_FACEBOOK_SECRET = "your-facebook-client-secret"
SOCIAL_AUTH_FACEBOOK_SCOPE = ["email", "publish_to_groups", "pages_manage_posts"]

SOCIAL_AUTH_INSTAGRAM_KEY = "your-instagram-client-id"
SOCIAL_AUTH_INSTAGRAM_SECRET = "your-instagram-client-secret"
SOCIAL_AUTH_INSTAGRAM_SCOPE = ["user_profile", "user_media"]

# Twitter OAuth
SOCIAL_AUTH_TWITTER_KEY = config("TWITTER_CLIENT_ID")
SOCIAL_AUTH_TWITTER_SECRET = config("TWITTER_CLIENT_SECRET")

# LinkedIn OAuth
SOCIAL_AUTH_LINKEDIN_KEY = "your-linkedin-client-id"
SOCIAL_AUTH_LINKEDIN_SECRET = "your-linkedin-client-secret"
SOCIAL_AUTH_LINKEDIN_SCOPE = ["r_liteprofile", "r_emailaddress", "w_member_social"]


# Celery settings
CELERY_BROKER_URL = config("CELERY_BROKER_URL")
CELERY_RESULT_BACKEND = config("CELERY_RESULT_BACKEND")


# CORS_ALLOWED_ORIGINS = [
#     "http://localhost:3000",  # Add your front-end URL here
#     "http://127.0.0.1:8000",
# ]

# Alternatively, to allow all origins (useful for development purposes)
CORS_ALLOW_ALL_ORIGINS = True

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
        },
        "file": {
            "level": "DEBUG",
            "class": "logging.FileHandler",
            "filename": "django_q.log",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "DEBUG",
    },
    "loggers": {
        "": {
            "handlers": ["console"],
            "level": "DEBUG",
            "propagate": True,
        },
        "django_q": {
            "handlers": ["file"],
            "level": "DEBUG",
            "propagate": True,
        },
    },
}


# Django-Q configuration
Q_CLUSTER = {
    "name": "DjangoQ",
    "workers": 4,
    "recycle": 500,
    "timeout": 60,
    "ack_failures": True,
    "max_attempts": 3,
    "retry": 3600,
    "queue_limit": 50,
    "bulk": 10,
    "orm": "default",
    "broker": "amqp://guest:guest@localhost:5672//",  # RabbitMQ URL
}
