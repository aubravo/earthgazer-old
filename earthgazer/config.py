from dataclasses import dataclass
import earthgazer.bigquery.config as bigquery_conf
import earthgazer.pipeline.config as pipeline_conf
import earthgazer.redis_connection.config as redis_conf
import earthgazer.task_broker.config as task_broker_conf
import earthgazer.webapp.config as webapp_config
import earthgazer.worker.config as worker_config
import dacite


@dataclass
class Configuration:
    bigquery = bigquery_conf.Configuration
    pipeline = pipeline_conf.Configuration
    redis = redis_conf.Configuration
    task_broker = task_broker_conf.Configuration
    webapp = webapp_config.Configuration
    worker = worker_config.Configuration

