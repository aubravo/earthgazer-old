"""Database Interface.
Include the project database management tools constructed with SQLAlchemy+dataclasses for ease of data management."""

import logging
from typing import List, Any

from sqlalchemy import create_engine, exc
from sqlalchemy.engine import URL, Engine
from sqlalchemy.orm import Session

import gxiba.data_objects

logger = logging.getLogger(__name__)


class DataBaseEngine:
    """DataBaseInterface
     Generate the required engine for interfacing with the project database.
     Defaults to sqlite to allow for local testing."""
    supported_databases = ['sqlite', 'oracle', 'mssql', 'mysql', 'firebird', 'postgresql', 'sybase']

    def __init__(self, kind: str = 'sqlite', username: str = None, password: str = None, host: str = None,
                 port: str = None, database: str = 'gxiba.db', echo=False, force_engine_generation=False,
                 ignore_duplicates=True, *args, **kwargs):
        self.ignore_duplicates = ignore_duplicates
        if force_engine_generation and (kind not in self.supported_databases):
            raise Exception(f'Database {kind} not supported.')
        url = URL.create(kind, username=username, password=password, host=host, port=port, database=database)
        logger.debug(f'Creating connection engine with {url}.')
        self._engine = create_engine(url, echo=echo, future=True)
        logger.debug('Binding to database and creating defined objects.')
        gxiba.data_objects.mapper_registry.metadata.create_all(bind=self._engine, checkfirst=True)
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
            except exc.IntegrityError as e:
                if 'duplicate' in str(e) and self.ignore_duplicates:
                    logger.error(f'Record {record} already in database.')
                    self.session.rollback()
                else:
                    raise
            except Exception as e:
                self.session.rollback()
                raise Exception(f'Error while attempting to add {record} into database: {e}')
