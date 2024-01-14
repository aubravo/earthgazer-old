import logging
from pathlib import Path
from typing import Optional

from pydantic import field_validator
from pydantic import model_validator
from pydantic_settings import BaseSettings
from pydantic_settings import SettingsConfigDict
from sqlalchemy import URL

logging.basicConfig(level=logging.DEBUG)


class FileManagerSettings(BaseSettings, extra="allow"):
    protocol: str
    base_path: Optional[str] = "/"


class DatabaseManagerSettings(BaseSettings, extra="allow"):
    drivername: str = "sqlite"
    username: Optional[str] = None
    password: Optional[str] = None
    host: Optional[str] = None
    port: Optional[int] = None
    database: Optional[str] = None
    url: Optional[URL] = None
    echo_sql: Optional[bool] = False

    @model_validator(mode="after")
    def validate_url(self):
        if not self.url:
            _url = URL.create(
                drivername=self.drivername,
                username=self.username,
                password=self.password,
                host=self.host,
                port=self.port,
                database=self.database,
            )
            logging.debug("Derivating URL")
            self.url = _url
        elif type(self.url) is str:
            logging.debug("Parsing URL")
            self.url = URL.create(self.url)
        return self


class EarthGazerSettings(BaseSettings):
    config_path: Path = Path(Path.home() / ".eg")
    database_manager: DatabaseManagerSettings = DatabaseManagerSettings()
    file_manager: dict[str, FileManagerSettings] = {}
    model_config = SettingsConfigDict(env_file=".env", env_nested_delimiter="__", env_prefix="earthgazer__")

    @field_validator("config_path")
    @classmethod
    def path_validator(cls, path: Path):
        path.mkdir(parents=True, exist_ok=True)
