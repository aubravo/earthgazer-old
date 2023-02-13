from pydantic import BaseModel, Field


class Configuration(BaseModel):
    drivername: str = 'postgresql'
    host: str = 'localhost'
    port: int = 5432
    username: str = 'postgres'
    password: str = ''
    _schema: str = Field('', alias='schema')
    database: str = 'postgres'
