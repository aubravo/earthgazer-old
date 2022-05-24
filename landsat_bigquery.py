import os
from common.sql_queries import landsat_bigquery, landsat_insert_query
from common.postgres_connector import PgHandler
from common.bigquery_connector import BQHandler

y = BQHandler()
x = PgHandler()


for row in y.query(landsat_bigquery):
    x.execute(landsat_insert_query,
              landsat_id=row[0],
              sensing_time=row[1].isoformat(),
              north_lat=row[2],
              south_lat=row[3],
              west_lon=row[4],
              east_lon=row[5],
              status="testing",
              base_url=row[6],
              )
    """
    os.system(r"gsutil -m rsync -r -x '^(?!.*B[0-9]+\.TIF$).*' {} gs://gxiba-1/LANDSAT/{}/".format(row[2], row[0]))
    print("Process complete for {}".format(row[0]))
    """

