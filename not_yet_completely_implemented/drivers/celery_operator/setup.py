from celery import Celery

from earthgazer.redis_operator.setup import REDIS
from earthgazer.setup import GXIBA_CONFIGURATION

if GXIBA_CONFIGURATION.celery.use_redis_as_backend:
    CELERY_APP = Celery('earthgazer', broker=REDIS.BROKER_URL, backend=REDIS.BACKEND_URL)
else:
    CELERY_APP = Celery('earthgazer', broker=REDIS.BROKER_URL)

CELERY_APP.conf.broker_transport_options = {'visibility_timeout': GXIBA_CONFIGURATION.celery.visibility_timeout}
