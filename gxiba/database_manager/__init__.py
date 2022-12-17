"""Database manager.

This module provides the required tools for working with the project database.
WARNING: This works with SQLite as default for local testing, a different is recommended in to guarantee stability and
data persistence.
"""

import logging
from typing import Protocol


class DataBaseEngine(Protocol):
    _engine: None

    @property
    def engine(self):
        return self._engine
    ...


class DataBaseManager:
    def __init__(self, database_engine: DataBaseEngine):
        self.database_engine = database_engine()

    def query(self):
        ...
