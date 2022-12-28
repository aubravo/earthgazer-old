"""Database Interface.

This module provides the required tools for working with the project database."""
import logging
# Included libraries.
from typing import List

# 3rd party libraries.
from sqlalchemy import create_engine
from sqlalchemy.engine import URL
from sqlalchemy.orm import Session

# Own libraries.
# mapper_registry is required as it inherits the dataclasses construction and
# thus allows for the setup of the right tables in the provided database.
from gxiba.data_objects import mapper_registry, GxibaImageMetadata


class DataBaseInterface:
    """DataBaseInterfaces generates the required engine for interfacing with the provided database.
    Defaults to sqlite to allow for local testing. Not recommended for production!
    """
    supported_databases = ['sqlite', 'oracle', 'mssql', 'mysql', 'firebird', 'postgresql', 'sybase']

    def __init__(self, database_type: str = 'sqlite', username: str = None, password: str = None, host: str = None,
                 port: str = None, database: str = 'gxiba.db', echo=False):
        if database_type not in self.supported_databases:
            raise Exception(
                f'Database {database_type} not supported. Select one of {", ".join(self.supported_databases)}')
        if database_type == 'sqlite':
            logging.warning('SQLite database recommended only for testing purposes.')
        logging.debug('Creating database engine URL.')
        self.url = URL.create(database_type,
                              username=username, password=password,
                              host=host, port=port,
                              database=database)
        logging.debug('Creating connection engine.')
        self._engine = create_engine(self.url, echo=echo, future=True)
        logging.debug('Binding to database and creating defined objects.')
        mapper_registry.metadata.create_all(bind=self._engine, checkfirst=True)
        self._session = Session(self._engine)

    @property
    def session(self) -> Session:
        return self._session

    @property
    def engine(self):
        return self._engine

    def add(self, objects: List[GxibaImageMetadata] | GxibaImageMetadata):
        if isinstance(objects, List):
            self.session.add_all(objects)
            self.session.commit()
        if isinstance(objects, GxibaImageMetadata):
            self.session.add_all([objects])
            self.session.commit()
