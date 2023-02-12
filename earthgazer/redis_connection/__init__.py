import logging
from urllib import parse

import redis

logging.basicConfig(level=logging.DEBUG)


class Redis:
    mq_db_number = 10
    backend_db_number = 11
    config_db_number = 12

    def __init__(self, redis_url):
        try:
            parse.urlparse(redis_url)
        except Exception:
            raise Exception('Invalid Redis URL.')
        self.MQ = redis.from_url(f'{redis_url}/{self.mq_db_number}')
        self.BACKEND = redis.from_url(f'{redis_url}/{self.backend_db_number}')
        self.CONFIG = redis.from_url(f'{redis_url}/{self.config_db_number}')

    def test(self):
        logging.info(self.MQ.ping())
        logging.info(self.BACKEND.ping())
        logging.info(self.CONFIG.ping())


if __name__ == '__main__':
    from earthgazer.config import Configuration
    REDIS = Redis(Configuration.redis.redis_url)
    REDIS.test()
