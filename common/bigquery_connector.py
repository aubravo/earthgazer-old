from google.cloud import bigquery
from google.oauth2 import service_account


class BQHandler:
    def __init__(self):
        key_path = "./keys.json"
        credentials = service_account.Credentials.from_service_account_file(
            key_path, scopes=["https://www.googleapis.com/auth/cloud-platform"],
        )
        self.client = bigquery.Client(credentials=credentials, project=credentials.project_id)
        self.job_config = bigquery.QueryJobConfig(use_query_cache=False)

    def query(self, query):
        return self.client.query(query, job_config=self.job_config)
