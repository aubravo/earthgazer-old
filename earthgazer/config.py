from pydantic import BaseModel

from earthgazer.bigquery import config as bigquery_conf
from earthgazer.celery_manager import config as celery_conf
from earthgazer.database import config as database_conf
from earthgazer.pipeline import config as pipeline_conf
from earthgazer.redis_connection import config as redis_conf
from earthgazer.task_broker import config as task_broker_conf
from earthgazer.webapp import config as webapp_config
from earthgazer.worker import config as worker_config


class Configuration(BaseModel):
    bigquery: bigquery_conf.Configuration
    celery: celery_conf.Configuration
    database: database_conf.Configuration
    pipeline: pipeline_conf.Configuration
    redis: redis_conf.Configuration
    task_broker: task_broker_conf.Configuration
    webapp: webapp_config.Configuration
    worker: worker_config.Configuration
