"""Database Interface.

This module provides the required tools for working with the project database."""

# Included libraries
from typing import List

# 3rd party libraries
from sqlalchemy import create_engine
from sqlalchemy.engine import URL
from sqlalchemy.orm import Session

# Own libraries
from gxiba.data_objects import mapper_registry, GxibaImageMetadata


class DataBaseInterface:
    supported_databases = ['sqlite', 'oracle', 'mssql', 'mysql', 'firebird', 'postgresql', 'sybase']

    def __init__(self, database_type: str = 'sqlite', username: str = None, password: str = None, host: str = None,
                 port: str = None, database: str = 'gxiba.db', echo=False):
        if database_type not in self.supported_databases:
            raise Exception(
                f'Database {database_type} not supported. Select one of {", ".join(self.supported_databases)}')

        self.url = URL.create(database_type, username=username, password=password, host=host, port=port,
                              database=database)
        self._engine = create_engine(self.url, echo=echo, future=True)
        mapper_registry.metadata.create_all(bind=self._engine, checkfirst=True)
        self._session = Session(self._engine)

    @property
    def session(self):
        return self._session

    @property
    def engine(self):
        return self._engine

    def add(self, objects: List[GxibaImageMetadata] | GxibaImageMetadata):
        if isinstance(objects, List):
            self._session.add_all(objects)
            self._session.commit()
        if isinstance(objects, GxibaImageMetadata):
            self._session.add_all([objects])
            self._session.commit()

    def __delete__(self, instance):
        self._session.close()
        del self._session

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._session.close()
        del self._session
