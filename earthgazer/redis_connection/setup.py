import logging
from urllib import parse

import redis
from earthgazer.config import Configuration
logging.basicConfig(level=logging.DEBUG)


class Redis:
    broker_db_number = 10
    backend_db_number = 11
    config_db_number = 12

    def __init__(self, redis_url):
        try:
            parse.urlparse(redis_url)
        except Exception:
            raise Exception('Invalid Redis URL.')
        self.BROKER = redis.from_url(f'{redis_url}/{self.broker_db_number}')
        self.BACKEND = redis.from_url(f'{redis_url}/{self.backend_db_number}')
        self.CONFIG = redis.from_url(f'{redis_url}/{self.config_db_number}')

    def test(self):
        logging.info(self.BROKER.ping())
        logging.info(self.BACKEND.ping())
        logging.info(self.CONFIG.ping())


REDIS = Redis(Configuration.redis.redis_url)
REDIS.test()
