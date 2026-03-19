import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'DICAS_PROJECT.settings')

app = Celery('DICAS_PROJECT')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()
