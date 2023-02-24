import enum

from pydantic import BaseSettings


class DuplicateHandling(enum.Enum):
    ignore = 'ignore'


class Configuration(BaseSettings):
    storage_driver: str = 'GCSDriver'
    duplicate_handling: DuplicateHandling = DuplicateHandling.ignore
