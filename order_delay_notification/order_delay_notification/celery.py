from __future__ import absolute_import, unicode_literals
import os

from celery import Celery
from django.conf import settings


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'order_delay_notification.settings')


app = Celery("order_delay_notification")
app.config_from_object('django.conf:settings', namespace='CELERY')

# app.conf.enable_utc = False

# app.conf.update(timezone = 'Asia/Kolkata')

# Celery Beat Settings
app.autodiscover_tasks()


@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')