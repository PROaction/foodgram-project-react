import os

from django.core.wsgi import get_wsgi_application


# ew
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'foodgram_backend.settings')

application = get_wsgi_application()
