from google.cloud import bigquery
from google.oauth2 import service_account

from earthgazer.setup import GXIBA_CONFIGURATION


class BigQueryInterface:
    """BigQueryInterface returns an object that allows for the querying of Google's BigQuery datasets."""

    def __init__(self, credentials: dict):
        """Creates the Google BigQuery Client object to allow for queries through the query method."""
        self.service_account_credentials = service_account.Credentials.from_service_account_info(
            credentials, scopes=["https://www.googleapis.com/auth/cloud-platform"])
        self._client = bigquery.Client(credentials=self.service_account_credentials,
                                       project=self.service_account_credentials.project_id)

    @property
    def client(self):
        return self._client

    def query(self, query):
        return self._client.query(query)


GXIBA_BIGQUERY_INTERFACE = BigQueryInterface(GXIBA_CONFIGURATION.bigquery.service_account_credentials)
