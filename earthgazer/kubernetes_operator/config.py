from pydantic import BaseSettings, RedisDsn


class Configuration(BaseSettings):
    use_kube_config_file: bool = True

