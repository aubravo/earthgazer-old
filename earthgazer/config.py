""" earthgazer/config.py is part of earthgazer.

    earthgazer is free software: you can redistribute it and/or modify it under the terms
    of the GNU General Public License as published by the Free Software Foundation, either
    version 3 of the License, or (at your option) any later version.

    earthgazer is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
    without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
     See the GNU General Public License for more details.

    You should have received a copy of the GNU General Public License along with earthgazer.
     If not, see <https://www.gnu.org/licenses/>.


    earthgazer/config.py merges the configuration files of all the sub-parts of the project.
    By using pydantic BaseSetting class, it allows for different ways to interact with project settings.
    """

from pydantic import BaseSettings

from earthgazer.bigquery_operator import config as bigquery_config
from earthgazer.celery_operator import config as celery_config
from earthgazer.kubernetes_operator import config as k8s_config
from earthgazer.pipeline import config as pipeline_config
from earthgazer.redis_operator import config as redis_config
from earthgazer.task_broker import config as task_broker_config
from earthgazer.webapp import config as webapp_config
from earthgazer.worker import config as worker_config


class Configuration(BaseSettings):
    bigquery: bigquery_config.Configuration = bigquery_config.Configuration()
    celery: celery_config.Configuration = celery_config.Configuration()
    k8s: k8s_config.Configuration = k8s_config.Configuration()
    pipeline: pipeline_config.Configuration = pipeline_config.Configuration()
    redis: redis_config.Configuration = redis_config.Configuration()
    task_broker: task_broker_config.Configuration = task_broker_config.Configuration()
    webapp: webapp_config.Configuration = webapp_config.Configuration()
    worker: worker_config.Configuration = worker_config.Configuration()

    class Config:
        env_nested_delimiter = '__'
