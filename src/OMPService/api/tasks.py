# Create your tasks here
from __future__ import absolute_import, unicode_literals
from celery import shared_task


@shared_task
def api_test(x, y):
    return int(x) + int(y)

