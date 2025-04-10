from pathlib import Path
import os
# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'ci!=nl9#v4x=ve#$($=!h=bd9t)kl&*1_e)v)^_ln3d2g#pqqj'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['10.87.86.50', 'localhost', '127.0.0.1', '*', 'http://45-61-54-80.cloud-xip.com:8000/']  # Agrega tu IP pública aquí

CSRF_TRUSTED_ORIGINS = [
    'https://<subdominio>.ngrok.io',  # Reemplaza con la URL generada por ngrok
    'https://localhost:8000',
    'https://pskcl74t-8000.use.devtunnels.ms/',
    'http://45-61-54-80.cloud-xip.com:8000/'
]

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'core',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'project.urls'

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

WSGI_APPLICATION = 'project.wsgi.application'


# Database
# https://docs.djangoproject.com/en/3.1/ref/settings/#databases

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': BASE_DIR / 'db.sqlite3',
#     }
# }
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql', 
        'NAME': 'faceapp',
        'USER': 'admin',
        'PASSWORD': 'contrasena08',
        'HOST': 'faceapp.c5eey42wm77i.us-east-2.rds.amazonaws.com', 
        'PORT': '3306',  
    }
}

# Password validation
# https://docs.djangoproject.com/en/3.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/3.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'America/Santiago'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# AWS S3 Configuration
AWS_ACCESS_KEY_ID = 'AKIA2MYIDRHYN45DVM5A'  # Verifica que esta clave sea correcta
AWS_SECRET_ACCESS_KEY = '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'  # Verifica que esta clave sea correcta
AWS_STORAGE_BUCKET_NAME = 'archivosfaceapp'  # Verifica que el nombre del bucket sea correcto
AWS_S3_REGION_NAME = 'us-east-2'  # Verifica que la región sea correcta
AWS_QUERYSTRING_AUTH = False  # Desactiva las URLs firmadas para archivos públicos
AWS_S3_SIGNATURE_VERSION = 's3v4'

# Static files (CSS, JavaScript, Images)
STATIC_URL = f'https://{AWS_STORAGE_BUCKET_NAME}.s3.{AWS_S3_REGION_NAME}.amazonaws.com/static/'
STATICFILES_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'

# Media files
MEDIA_URL = f'https://{AWS_STORAGE_BUCKET_NAME}.s3.{AWS_S3_REGION_NAME}.amazonaws.com/media/'
DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.1/howto/static-files/

# STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'

# STATICFILES_DIRS = (
#     os.path.join(BASE_DIR, "static"),
# )
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')  # Directorio temporal para collectstatic
# MEDIA_ROOT = os.path.join(BASE_DIR, 'media/')

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

        'file': {
            'level': 'WARNING',
            'class': 'logging.FileHandler',
            'filename': 'debug.log',
            'formatter': 'verbose',
        },

        'console': {
            'level': 'WARNING',
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
    },

    'loggers': {

        'django': {
            'handlers': ['file', 'console'],
            'level': 'WARNING',
            'propagate': True,
        },
 
        
        'face_attendance': {  
            'handlers': ['file'],
            'level': 'WARNING',
            'propagate': True,
        },

    },
}