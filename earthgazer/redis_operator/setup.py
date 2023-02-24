import logging
from urllib import parse

import redis

from earthgazer.setup import GXIBA_CONFIGURATION

logging.basicConfig(level=logging.DEBUG)


class Redis:
    earthgazer_db_number = GXIBA_CONFIGURATION.redis.earthgazer_db_number
    broker_db_number = GXIBA_CONFIGURATION.redis.broker_db_number
    backend_db_number = GXIBA_CONFIGURATION.redis.backend_db_number
    config_db_number = GXIBA_CONFIGURATION.redis.config_db_number

    def __init__(self, redis_url):
        try:
            parse.urlparse(redis_url)
        except Exception:
            raise Exception('Invalid Redis URL.')

        self.EARTHGAZER_URL = f'{redis_url}/{self.broker_db_number}'
        self.EARTHGAZER = redis.from_url(f'{redis_url}/{self.broker_db_number}')
        self.BROKER_URL = f'{redis_url}/{self.broker_db_number}'
        self.BROKER = redis.from_url(self.BROKER_URL)
        self.BACKEND_URL = f'{redis_url}/{self.backend_db_number}'
        self.BACKEND = redis.from_url(self.BACKEND_URL)
        self.CONFIG_URL = f'{redis_url}/{self.config_db_number}'
        self.CONFIG = redis.from_url(self.CONFIG_URL)

    def test(self):
        logging.info(f'CONNECTED TO EARTHGAZER DATABASE: {self.EARTHGAZER.ping()}')
        logging.info(f'CONNECTED TO BROKER DATABASE: {self.BROKER.ping()}')
        logging.info(f'CONNECTED TO BACKEND DATABASE: {self.BACKEND.ping()}')
        logging.info(f'CONNECTED TO CONFIGURATION DATABASE:{self.CONFIG.ping()}')


REDIS = Redis(GXIBA_CONFIGURATION.redis.redis_url)
REDIS.test()
