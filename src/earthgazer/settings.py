import logging
from pathlib import Path
from typing import ClassVar
from typing_extensions import Annotated
from pydantic import field_validator
from pydantic import model_validator
from pydantic import Field
from pydantic_settings import BaseSettings
from pydantic_settings import SettingsConfigDict
from sqlalchemy import URL

logging.basicConfig(level=logging.DEBUG)


class FileManagerSettings(BaseSettings, extra="allow"):
    protocol: str
    base_path: str | None = "/"


class DatabaseManagerSettings(BaseSettings, extra="allow"):
    drivername: str = "sqlite"
    username: str | None = None
    password: str | None = None
    host: str | None = None
    port: int | None = None
    database: str | None = None
    url: URL | str | None = None
    echo_sql: bool | None = False

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
        elif isinstance(self.url, str):
            logging.debug("Parsing URL")
            self.url = URL.create(self.url)
        return self


class EarthGazerSettings(BaseSettings):
    config_path: Annotated[str, Field(validate_default=True)] = str(Path(Path.home() / ".eg"))
    database_manager: DatabaseManagerSettings = DatabaseManagerSettings()
    file_manager: ClassVar[dict[str, FileManagerSettings]] = {}
    model_config = SettingsConfigDict(env_file=".env", env_nested_delimiter="__", env_prefix="earthgazer__")

    @field_validator("config_path")
    @classmethod
    def path_validator(cls, path: str):
        abs_path = Path(path).expanduser().resolve()
        abs_path.mkdir(parents=True, exist_ok=True)
        return str(abs_path)
