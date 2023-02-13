from celery import Celery

from earthgazer.setup import GXIBA_CONFIGURATION
from earthgazer.redis_connection.setup import REDIS

if GXIBA_CONFIGURATION.celery.use_redis_as_backend:
    CELERY_APP = Celery('gxiba', broker=REDIS.BROKER, backend='redis:///11')


CELERY_APP.conf.broker_transport_options = {'visibility_timeout': 3600}


@CELERY_APP.task
def add(x, y):
    return x + y
