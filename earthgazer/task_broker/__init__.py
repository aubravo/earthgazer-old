from celery import Celery

CELERY_APP = Celery('gxiba', broker='redis:///10', backend='redis:///11')
CELERY_APP.conf.broker_transport_options = {'visibility_timeout': 3600}


@CELERY_APP.task
def add(x, y):
    return x + y
