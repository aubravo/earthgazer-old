import os
from toolbox.queries import landsat_get_queried, sentinel_get_queried, \
    landsat_change_status, sentinel_change_status
from toolbox.connectors import PgHandler
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s \t %(name)s \t %(levelname)s \t %(message)s")

pg_handler = PgHandler(host=os.getenv('DB_HOST'),
                       user=os.getenv('DB_USER'),
                       password=os.getenv('DB_PASS'),
                       dbname=os.getenv('DB_NAME'))

for row in pg_handler.fetch(landsat_get_queried):
    logging.info('Attempting to sync {}'.format(row[0]))
    os.system(r"gsutil -m rsync -r -x '^(?!.*B[0-9]+\.TIF$).*' {} gs://gxiba/LANDSAT/{}/".format(row[1], row[0]))
    logging.info("Process complete for {}".format(row[0]))
    pg_handler.execute(landsat_change_status.format(row[0]))

for row in pg_handler.fetch(sentinel_get_queried):
    logging.info('Attempting to sync {}'.format(row[0]))
    os.system(r"gsutil -m rsync -r -x '^(?!.*B[0-9]+\.jp2$).*' {} gs://gxiba/SENTINEL/{}/".format(row[1], row[0]))
    logging.info("Process complete for {}".format(row[0]))
    pg_handler.execute(sentinel_change_status.format(row[0]))
