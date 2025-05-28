import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'habitos_proyecto.settings')

app = Celery('habitos_proyecto')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()