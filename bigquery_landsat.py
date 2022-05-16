"""
Este código realiza un BigQuery para obtener los códigos de imágen y su ubicación
en el bucket de la base de datos abierta de Landsat en Google Cloud y sincroniza
las fotografías de las banads para almacenarlas en el bucket del proyecto
"""


from google.cloud import bigquery
from google.oauth2 import service_account
import os

key_path = "/home/alvaro/tesis/keys.json"
credentials = service_account.Credentials.from_service_account_file(
    key_path, scopes=["https://www.googleapis.com/auth/cloud-platform"],
)

bigquery_client = bigquery.Client(credentials=credentials, project=credentials.project_id)
bigquery_job_config = bigquery.QueryJobConfig(use_query_cache=False)
sql = """
SELECT product_id, sensing_time, base_url
FROM bigquery-public-data.cloud_storage_geo_index.landsat_index
WHERE
spacecraft_id = "LANDSAT_8" AND
north_lat > 19.023463 AND
south_lat < 19.023463 AND
east_lon > -98.622686 AND
west_lon < -98.622686 AND
date_acquired > '2010-01-01'
"""

bigquery_job = bigquery_client.query(sql, job_config=bigquery_job_config)
for row in bigquery_job:
    os.system(r"gsutil -m rsync -r -x '^(?!.*B[0-9]+\.TIF$).*' {} gs://gxiba-1/LANDSAT/{}/".format(row[2], row[0]))
    print("Process complete for {}".format(row[0]))
