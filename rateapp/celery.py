from celery import Celery
import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rateapp.settings')

app = Celery('rateapp')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

app.conf.broker_url = 'redis://redis:6379/0'