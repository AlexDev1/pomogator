from __future__ import absolute_import
import os
import sys
from celery import Celery

PROJECT_PATH = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.abspath(os.path.join(PROJECT_PATH, '..')))
sys.path.append(os.path.abspath(os.path.join(PROJECT_PATH, '.')))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "pomogator.settings")

from django.conf import settings

app = Celery("pomogator")

app.config_from_object("django.conf:settings", namespace="CELERY")

app.conf.update(
    task_serializer='pickle',
    result_serializer='pickle',
    accept_content=['pickle']
)

app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)
