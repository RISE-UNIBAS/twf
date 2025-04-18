import os
import logging
from celery import Celery

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'transkribusWorkflow.settings')

app = Celery('transkribusWorkflow')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related config keys
#   should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django app configs.
app.autodiscover_tasks(['twf'])

logger = logging.getLogger(__name__)


@app.task(bind=True)
def debug_task(self):
    logger.debug('Request: %r', self.request)
