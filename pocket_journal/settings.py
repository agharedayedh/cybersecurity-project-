import os
from pathlib import Path
BASE_DIR = Path(__file__).resolve().parent.parent
SECRET_KEY = os.environ["DJANGO_SECRET_KEY"]
DEBUG = True  
ALLOWED_HOSTS = ['localhost','127.0.0.1','testserver']
INSTALLED_APPS = ['django.contrib.contenttypes','django.contrib.sessions','django.contrib.messages','django.contrib.staticfiles','journal']
MIDDLEWARE = ['django.middleware.security.SecurityMiddleware','django.contrib.sessions.middleware.SessionMiddleware','django.middleware.common.CommonMiddleware','django.middleware.csrf.CsrfViewMiddleware','django.contrib.messages.middleware.MessageMiddleware']
ROOT_URLCONF = 'pocket_journal.urls'
TEMPLATES = [{'BACKEND':'django.template.backends.django.DjangoTemplates','DIRS':[],'APP_DIRS':True,'OPTIONS':{'context_processors':['django.template.context_processors.request','django.contrib.messages.context_processors.messages']}}]
DATABASES = {'default': {'ENGINE':'django.db.backends.sqlite3','NAME':BASE_DIR/'db.sqlite3'}}
SESSION_COOKIE_HTTPONLY = True
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
STATIC_URL = 'static/'
# A09 FIX SUPPORT: log to console and local rotating file 
# LOGGING = {
#     'version': 1, 'disable_existing_loggers': False,
#     'formatters': {'security': {'format': '%(asctime)s %(levelname)s %(message)s'}},
#     'handlers': {
#         'console': {'class': 'logging.StreamHandler','formatter':'security'},
#         'security_file': {'class':'logging.handlers.RotatingFileHandler',
#                           'filename': str(BASE_DIR/'security.log'),
#                           'maxBytes': 1000000, 'backupCount': 3,
#                           'formatter':'security'},
#     },
#     'loggers': {'journal.security': {'handlers':['console','security_file'],
#                                    'level':'WARNING','propagate':False}},
# }
