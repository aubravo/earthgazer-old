"""Database manager.

This module provides the required tools for working with the project database.
WARNING: This works with SQLite as default for local testing, a different is recommended in to guarantee stability and
data persistence.
"""

import sqlite3
from enum import Enum, auto
import logging


class DataBaseManager:
    class DBEngine(Enum):
        SQLITE = auto()
        POSTGRES = auto()

    def __init__(self, database_engine: DBEngine = DBEngine.SQLITE):
        if database_engine == self.DBEngine.SQLITE:
            logging.warning('SQLite is selected as Database Engine. This is recommended only for testing purposes.')
        self.engine_ = database_engine

    def query(self):
        ...
