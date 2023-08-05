from pydantic import BaseSettings


class Configuration(BaseSettings):
    use_redis_as_backend: bool = True
    visibility_timeout: int = 3600

