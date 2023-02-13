from pydantic import BaseModel


class Configuration(BaseModel):
    redis_url: str = 'redis://'
