from google.oauth2 import service_account
from google.cloud import bigquery, storage
import psycopg2
import logging
import json


class PgHandler:
    def __init__(self, host="localhost", port=5432, user="postgres", password="", dbname=""):
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.dbname = dbname

        logging.info('Attempting to connect to {} in {}:{} with user {}'.format(dbname, host, port, user))
        self.conn = psycopg2.connect(
            host=self.host,
            database=self.dbname,
            user=self.user,
            password=self.password
        )

    def __del__(self):
        try:
            self.conn.close()
        except Exception as e:
            logging.warning("Connection could not be closed: {}".format(e))

    def execute(self, sql_statement, _dict=None):
        cursor = self.conn.cursor()
        cursor.execute(sql_statement, _dict)
        self.conn.commit()

    def fetch(self, sql_statement, _dict=None):
        cursor = self.conn.cursor()
        cursor.execute(sql_statement, _dict)
        return cursor.fetchall()


class BQHandler:
    def __init__(self, keypath="./keys.json", keys=None):
        try:
            if keys is not None:
                credentials = service_account.Credentials.from_service_account_info(
                    json.loads(keys))
            else:
                credentials = service_account.Credentials.from_service_account_file(
                    keypath, scopes=["https://www.googleapis.com/auth/cloud-platform"],
                )
        except Exception as e:
            raise Exception(e)
        self.client = bigquery.Client(credentials=credentials, project=credentials.project_id)
        self.job_config = bigquery.QueryJobConfig(use_query_cache=False)

    def query(self, query):
        return self.client.query(query, job_config=self.job_config)


