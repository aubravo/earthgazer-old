"""BigQuery

This module contains the class BigQueryInterface which acts as an interface for importing the satellite
image metadata from the Google Cloud Sentinel-2 and Landsat open data projects, thus allowing to gather
the Google Storage Buckets path for each of the images of interest, as well as the rest of the images
metadata such as platform_id, sensing_time, longitude and latitude."""

from google.cloud import bigquery
from google.oauth2 import service_account


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
        """Returns the BigQuery client object to allow the google.cloud.bigquery.Client methods to be executed."""
        return self._client

    def query(self, query):
        """Returns an iterable with the results of the query."""
        return self._client.query(query)
