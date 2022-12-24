from google.cloud import bigquery
from google.oauth2 import service_account

BIGQUERY_PATH_SENTINEL_2 = "bigquery-public-data.cloud_storage_geo_index.sentinel_2_index"
BIGQUERY_PATH_LANDSAT_8 = "bigquery-public-data.cloud_storage_geo_index.landsat_index"


class BigQueryInterface:
    def __init__(self, credentials: dict):
        self.service_account_credentials = service_account.Credentials.from_service_account_info(
            credentials,
            scopes=["https://www.googleapis.com/auth/cloud-platform"]
        )
        self.client = bigquery.Client(credentials=self.service_account_credentials,
                                      project=self.service_account_credentials.project_id)

    def query(self, query):
        return self.client.query(query)
