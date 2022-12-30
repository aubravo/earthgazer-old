"""Database Interface.
Include the project database management tools constructed with SQLAlchemy+dataclasses for ease of data management."""

import logging
from typing import List, Any
from sqlalchemy import create_engine
from sqlalchemy.engine import URL, Engine
from sqlalchemy.orm import Session
import gxiba.data_objects.image_metadata as gxiba_metadata


class DataBaseInterface:
    """DataBaseInterface
     Generate the required engine for interfacing with the project database.
     Defaults to sqlite to allow for local testing."""
    supported_databases = ['sqlite', 'oracle', 'mssql', 'mysql', 'firebird', 'postgresql', 'sybase']

    def __init__(self, database_kind: str = 'sqlite', username: str = None, password: str = None, host: str = None,
                 port: str = None, database: str = 'gxiba.db', echo=False, force_engine_generation=False):
        if force_engine_generation and (database_kind not in self.supported_databases):
            raise Exception(f'Database {database_kind} not supported.')
        url = URL.create(database_kind, username=username, password=password, host=host, port=port, database=database)
        logging.debug(f'Creating connection engine with {url}.')
        self._engine = create_engine(url, echo=echo, future=True)
        logging.debug('Binding to database and creating defined objects.')
        gxiba_metadata.mapper_registry.metadata.create_all(bind=self._engine, checkfirst=True)
        self._session = Session(self._engine)

    @property
    def session(self) -> Session:
        return self._session

    @property
    def engine(self) -> Engine:
        return self._engine

    def add(self, record: Any):
        if isinstance(record, List):
            try:
                self.session.add_all(record)
                self.session.commit()
            except Exception as e:
                self.session.rollback()
                raise Exception(f'Error while attempting to add {record} into database: {e}')
        else:
            try:
                self.session.add(record)
                self.session.commit()
            except Exception as e:
                self.session.rollback()
                raise Exception(f'Error while attempting to add {record} into database: {e}')
