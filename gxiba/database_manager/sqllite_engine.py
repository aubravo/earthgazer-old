import logging
import sqlite3
import pandas

from gxiba.database_manager import DataBaseEngine


class SQLiteDataBaseEngine(DataBaseEngine):
    def __init__(self, database_path):
        self.connection = None
        self.cursor = None
        super().__init__(database_path)

    def setup(self) -> None:
        self.connection = self._engine = sqlite3.connect(self.database_path)
        self.cursor = self.connection.cursor()
        self.setup_gxiba_table()

    def setup_gxiba_table(self):
        self.execute("""CREATE TABLE IF NOT EXISTS gxiba_images
                        (   id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                            platform TEXT,
                            platform_id TEXT,
                            sensing_time TEXT,
                            latitude_north REAL,
                            latitude_south REAL,
                            longitude_west REAL,
                            longitude_east REAL,
                            base_url TEXT,
                            status TEXT                                     ); """)

    def query(self, sql_query) -> pandas.DataFrame:
        return pandas.read_sql_query(sql=sql_query, con=self.engine)

    def execute(self, sql_query) -> None:
        self.cursor.execute(sql_query)
        if self.cursor.fetchone() is not None:
            logging.warning(f"execute() should return none. Try using query() instead.")
        self.connection.commit()

    def close(self):
        self.connection.close()

    def __delete__(self):
        self.connection.close()
