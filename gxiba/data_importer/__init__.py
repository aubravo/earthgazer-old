from google.cloud import bigquery
from google.oauth2 import service_account

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
