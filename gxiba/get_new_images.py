import os
from gxiba.toolbox.queries import landsat_bigquery, sentinel_bigquery,\
    landsat_insert, sentinel_insert, \
    landsat_get_most_recent_date, sentinel_get_most_recent_date
from gxiba.toolbox.connectors import BQHandler, PgHandler
from psycopg2.errors import UniqueViolation
import logging
import datetime

logging.basicConfig(level=logging.INFO, format="%(asctime)s \t %(name)s \t %(levelname)s \t %(message)s")

bq_handler = BQHandler(keys=os.getenv('SERVICEACCOUNTKEYS'))
pg_handler = PgHandler(host=os.getenv('DB_HOST'),
                       user=os.getenv('DB_USER'),
                       password=os.getenv('DB_PASS'),
                       dbname=os.getenv('DB_NAME'))

try:
    date_acquired = pg_handler.fetch(landsat_get_most_recent_date)[0][0].date().isoformat()
    logging.info('Fetched latest date')
except IndexError:
    date_acquired = datetime.datetime(1980, 1, 1).date().isoformat()
    logging.info('No dates found')

logging.info('Using start date: {}'.format(date_acquired))

for row in bq_handler.query(landsat_bigquery.format(date_acquired)):
    try:
        logging.info('Attempting to insert {}'.format(row[0]))
        pg_handler.execute(landsat_insert,
                           {"landsat_id": row[0],
                            "sensing_time": row[1].isoformat(),
                            "north_lat": row[2],
                            "south_lat": row[3],
                            "west_lon": row[4],
                            "east_lon": row[5],
                            "status": 'QUERIED',
                            "base_url": row[6]}
                           )
        logging.info('Successfully inserted {}'.format(row[0]))
    except UniqueViolation:
        logging.info('{} already in database'.format(row[0]))
    except Exception as e:
        logging.critical('Something went wrong while trying to insert {}: {}'.format(row[0], e))


try:
    date_acquired = pg_handler.fetch(sentinel_get_most_recent_date)[0][0].date().isoformat()
    logging.info('Fetched latest date')
except IndexError:
    date_acquired = datetime.datetime(1980, 1, 1).date().isoformat()
    logging.info('No dates found')

logging.info('Using start date: {}'.format(date_acquired))

for row in bq_handler.query(sentinel_bigquery.format(date_acquired)):
    try:
        logging.info('Attempting to insert {}'.format(row[0]))
        pg_handler.execute(sentinel_insert,
                           {"sentinel_id": row[0],
                            "product": row[1],
                            "sensing_time": row[2].isoformat(),
                            "north_lat": row[3],
                            "south_lat": row[4],
                            "west_lon": row[5],
                            "east_lon": row[6],
                            "status": 'QUERIED',
                            "base_url": row[7]}
                           )
        logging.info('Successfully inserted {}'.format(row[0]))
    except UniqueViolation:
        logging.info('{} already in database'.format(row[0]))
    except Exception as e:
        logging.critical('Something went wrong while trying to insert {}: {}'.format(row[0], e))


