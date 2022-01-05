from __future__ import absolute_import, unicode_literals
import os

from celery import Celery
from django.conf import settings
from celery.schedules import crontab

os.environ.setdefault(
    'DJANGO_SETTINGS_MODULE',
    'AHnalyzer.settings')

app = Celery('AHnalyzer')
app.conf.enable_utc = False

app.conf.update(timezone='Europe/Warsaw')

app.config_from_object(settings, namespace='CELERY')

# celery beat settings
app.conf.beat_schedule = {
    'test': {
        'task': 'items.tasks.test',
        'schedule': crontab(hour='*/12', minute=0),
    },
    'fill-data': {
        'task': 'items.tasks.fill_data_auctions',
        'schedule': crontab(hour=14, minute=9),
    },
}

app.autodiscover_tasks()

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')