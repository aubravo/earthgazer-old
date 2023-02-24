from pydantic import BaseSettings, RedisDsn


class Configuration(BaseSettings):
    redis_url: RedisDsn = 'redis://'
    earthgazer_db_number: int = 5
    broker_db_number: int = 10
    backend_db_number: int = 11
    config_db_number: int = 12
