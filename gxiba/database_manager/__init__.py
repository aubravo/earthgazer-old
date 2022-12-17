"""Database manager.

This module provides the required tools for working with the project database.
WARNING: This works with SQLite as default for local testing, a different is recommended in to guarantee stability and
data persistence.
"""

from abc import abstractmethod

import pandas
from pandas import DataFrame
from typing import Protocol


class DataBaseEngine(Protocol):
    _engine: object
    database_path: str

    def __init__(self, database_path):
        self.database_path = database_path
        self.setup()

    @property
    def engine(self) -> object:
        return self._engine

    @abstractmethod
    def setup(self) -> None:
        ...

    @abstractmethod
    def query(self, sql_query) -> DataFrame:
        ...

    @abstractmethod
    def execute(self, sql_query) -> None:
        ...

    @abstractmethod
    def close(self) -> None:
        ...

    def __delete__(self, instance):
        self.close()


class DataBaseManager:
    def __init__(self, database_engine: DataBaseEngine, database_path: str):
        self.database_engine = database_engine(database_path)

    def query(self, sql_query) -> pandas.DataFrame:
        return self.database_engine.query(sql_query)

    def execute(self, sql_query):
        self.database_engine.execute(sql_query)

    def close(self):
        self.database_engine.close()

    def __delete__(self, instance):
        self.database_engine.close()
        del self.database_engine
