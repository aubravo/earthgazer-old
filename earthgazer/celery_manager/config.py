from pydantic import BaseModel


class Configuration(BaseModel):
    use_redis_as_backend: bool = False
    use_database_as_backend: bool = False
