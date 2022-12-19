from gxiba.database_manager import DataBaseEngine
import pandas


class PostgresDataBaseEngine(DataBaseEngine):
    def __init__(self, database_path):
        raise NotImplementedError

    def setup(self) -> None:
        raise NotImplementedError

    def query(self, sql_query) -> pandas.DataFrame:
        raise NotImplementedError

    def execute(self, sql_query) -> None:
        raise NotImplementedError

    def close(self):
        raise NotImplementedError
