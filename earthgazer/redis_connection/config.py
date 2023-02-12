from dataclasses import dataclass


@dataclass
class Configuration:
    redis_url: str = 'redis://'
