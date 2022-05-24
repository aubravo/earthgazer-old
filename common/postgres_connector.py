from google.oauth2 import service_account
from google.cloud.sql.connector import Connector
import pg8000
import sqlalchemy


class PgHandler:
    def __init__(self):
        def get_conn() -> pg8000.dbapi.Connection:
            key_path = "./keys.json"
            credentials = service_account.Credentials.from_service_account_file(
                key_path, scopes=["https://www.googleapis.com/auth/cloud-platform"],
            )
            with Connector(credentials=credentials) as connector:
                conn = connector.connect(
                    "gxiba-1:us-central1:gxiba",
                    "pg8000",
                    user="gxiba-user@gxiba-1.iam",
                    enable_iam_auth=True,
                    db="gxibadev"
                )
            return conn
        self.pool = sqlalchemy.create_engine(
            "postgresql+pg8000://",
            creator=get_conn,
        )

    def execute(self, sql_statement, **kwargs):
        with self.pool.connect() as db_conn:
            db_conn.execute(sqlalchemy.text(sql_statement), **kwargs)

    def fetch(self, sql_statement, **kwargs):
        with self.pool.connect() as db_conn:
            return db_conn.execute(sqlalchemy.text(sql_statement), **kwargs).fetchall()
