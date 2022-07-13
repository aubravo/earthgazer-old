import os
from toolbox.queries import *
from google.oauth2 import service_account
from google.cloud import bigquery
import psycopg2
import logging
import json
from psycopg2.errors import UniqueViolation
import datetime
import luigi
from luigi.contrib.gcs import GCSClient, GCSTarget
import rasterio
import tempfile

logging.basicConfig(level=logging.INFO, format="%(asctime)s \t %(name)s \t %(levelname)s \t %(message)s")


def get_env_vars(required_vars):
    try:
        return {var: os.environ[var] for var in required_vars}
    except KeyError:
        raise KeyError('One or more of the required ENVIRONMENT VARIABLES was not found:\n{}'.format(required_vars))


class PgHandler:
    def __init__(self, host="localhost", port=5432, user="postgres", password="", dbname=""):
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.dbname = dbname

        logging.info('Attempting to connect to {} in {}:{} with user {}'.format(dbname, host, port, user))
        self.conn = psycopg2.connect(host=self.host, database=self.dbname, user=self.user, password=self.password)

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
    def __init__(self):
        self.client = bigquery.Client(credentials=credentials, project=credentials.project_id)
        self.job_config = bigquery.QueryJobConfig(use_query_cache=False)

    def query(self, query):
        return self.client.query(query, job_config=self.job_config)


sentinel_bands = {'B04': 'red',
                  'B03': 'green',
                  'B02': 'blue',
                  'B07': 'swir1',
                  'B11': 'swir2',
                  'B12': 'swir3'}
env_vars = get_env_vars(['DB_HOST', 'DB_USER', 'DB_PASS', 'DB_NAME','SERVICEACCOUNTKEYS'])
credentials = service_account.Credentials.from_service_account_info(
    json.loads(env_vars['SERVICEACCOUNTKEYS']),
    scopes=["https://www.googleapis.com/auth/cloud-platform"])
gcs_client = GCSClient(oauth_credentials=credentials)
main_pg_handler = PgHandler(host=env_vars['DB_HOST'],
                            user=env_vars['DB_USER'],
                            password=env_vars['DB_PASS'],
                            dbname=env_vars['DB_NAME'])


class SyncBuckets:
    def __init__(self, platform):
        if platform not in ['LANDSAT', 'SENTINEL']:
            raise KeyError('Platform not supported: {}'.format(platform))

        for row in main_pg_handler.fetch(get_by_status.format(platform.lower(), 'QUERIED')):
            logging.info('Attempting to sync {}:{}'.format(platform, row[0]))
            os.system(
                r"gsutil -m rsync -r -x '^(?!.*B[0-9]+\.TIF$).*' {} gs://gxiba/{}/{}/"
                .format(row[1], platform, row[0]))
            logging.info("Process complete for {}:{}".format(platform, row[0]))
            main_pg_handler.execute(change_status_by_id.format(platform.lower(), 'SYNCED', row[0]))


class GetNewImages:

    def __init__(self, platform):
        self.env_vars = get_env_vars(['DB_HOST', 'DB_USER', 'DB_PASS', 'DB_NAME', 'SERVICEACCOUNTKEYS'])
        self.bq_handler = BQHandler()

        if platform not in ['LANDSAT', 'SENTINEL']:
            raise KeyError('Platform not supported: {}'.format(platform))

        try:
            date_acquired = main_pg_handler.fetch(get_most_recent_date.format(
                platform.lower()))[0][0].date().isoformat()
            logging.info('Fetched latest date')
        except IndexError:
            date_acquired = datetime.datetime(1980, 1, 1).date().isoformat()
            logging.info('No dates found')

        logging.info('Using start date: {}'.format(date_acquired))

        if platform == 'LANDSAT':
            _query = landsat_bigquery.format(date_acquired)
        else:
            _query = sentinel_bigquery.format(date_acquired)

        for row in self.bq_handler.query(_query):
            try:
                logging.info('Attempting to insert {}:{}'.format(platform, row[0]))
                main_pg_handler.execute(platform_insert,
                                        {"platform": platform.lower(),
                                         "id": row[0],
                                         "sensing_time": row[1].isoformat(),
                                         "north_lat": row[2],
                                         "south_lat": row[3],
                                         "west_lon": row[4],
                                         "east_lon": row[5],
                                         "status": 'QUERIED',
                                         "base_url": row[6]
                                         })
                logging.info('Successfully inserted {}:{}'.format(platform, row[0]))
            except UniqueViolation:
                logging.info('{}:{} already in database'.format(platform, row[0]))
            except Exception as e:
                logging.critical('Something went wrong while trying to insert {}:{}\n\t{}'.format(platform, row[0], e))


class GetImages(luigi.ExternalTask):
    path = luigi.Parameter()

    def output(self):
        return GCSTarget(path=self.path, format=luigi.format.Nop, client=gcs_client)


class ImageMerge(luigi.Task):
    platform = luigi.Parameter()
    id = luigi.Parameter()
    image_bands = {}

    def requires(self):
        main_pg_handler.execute(change_status_by_id.format(self.platform.lower(), 'Processing', self.id))
        if self.platform == 'SENTINEL':
            file = gcs_client.listdir("gs://gxiba/SENTINEL/{}/".format(self.id))
            for filename in file:
                for band in sentinel_bands.keys():
                    if band in filename:
                        self.image_bands[sentinel_bands[band]] = filename
                        break
            if len(self.image_bands.keys()) < len(sentinel_bands.values()):
                differences = ''
                for missing_band in list(set(sentinel_bands.values()) - set(self.image_bands.keys())):
                    differences = differences + missing_band + ','
                main_pg_handler.execute(change_status_by_id.format(self.platform.lower(),
                                                                   'Missing Bands:{}'.format(differences), self.id))
            else:
                return {band: GetImages(path=self.image_bands[band]) for band in self.image_bands.keys()}

        elif self.platform == 'LANDSAT':
            for l in []:
                pass
        else:
            raise KeyError('Platform not supported: {}'.format(self.platform))

    def run(self):
        if self.platform == 'SENTINEL':
            with tempfile.TemporaryDirectory() as _dir:
                basedir = _dir.replace('\\', '/').replace('C:/', 'C://')
                print(basedir)
                with self.input()['red'].open() as r_gcs,\
                        self.input()['blue'].open() as b_gcs,\
                        self.input()['green'].open() as g_gcs,\
                        open(basedir + "/r_temp.jp2", 'wb') as r_t,\
                        open(basedir + "/g_temp.jp2", 'wb') as g_t,\
                        open(basedir + "/b_temp.jp2", 'wb') as b_t:
                    r_t.write(r_gcs.read())
                    g_t.write(g_gcs.read())
                    b_t.write(b_gcs.read())

                with rasterio.open(basedir + '/r_temp.jp2', driver='JP2OpenJPEG') as r_band,\
                    rasterio.open(basedir + '/g_temp.jp2', driver='JP2OpenJPEG') as g_band,\
                    rasterio.open(basedir + '/b_temp.jp2', driver='JP2OpenJPEG') as b_band,\
                    rasterio.open(basedir + '/rgb_temp.tiff', 'w+', driver='Gtiff', width=r_band.width, height=r_band.height, count=3,
                                  crs=r_band.crs, transform=r_band.transform, dtype='uint16') as rgb:
                    rgb.write(r_band.read(1), 1)
                    rgb.write(g_band.read(1), 2)
                    rgb.write(b_band.read(1), 3)

                gcs_client.put(basedir + '/rgb_temp.tiff',
                                "gs://gxiba/merged/SENTINEL/{}/{}_rgb.tiff".format(self.id, self.id))

                with self.input()['swir1'].open() as sw1_gcs,\
                        self.input()['swir2'].open() as sw2_gcs,\
                        self.input()['swir3'].open() as sw3_gcs,\
                        open(basedir + "/sw1_temp.jp2", 'wb') as sw1_t,\
                        open(basedir + "/sw2_temp.jp2", 'wb') as sw2_t,\
                        open(basedir + "/sw3_temp.jp2", 'wb') as sw3_t:
                    sw1_t.write(sw1_gcs.read())
                    sw2_t.write(sw2_gcs.read())
                    sw3_t.write(sw3_gcs.read())

                with rasterio.open(basedir + '/sw1_temp.jp2', driver='JP2OpenJPEG') as sw1_band,\
                    rasterio.open(basedir + '/sw2_temp.jp2', driver='JP2OpenJPEG') as sw2_band,\
                    rasterio.open(basedir + '/sw3_temp.jp2', driver='JP2OpenJPEG') as sw3_band,\
                    rasterio.open(basedir + '/swir_temp.tiff', 'w+', driver='Gtiff', width=sw1_band.width,
                                  height=sw1_band.height, count=3, crs=sw1_band.crs, transform=sw1_band.transform,
                                  dtype='uint16') as swir:
                    swir.write(sw1_band.read(1), 1)
                    swir.write(sw2_band.read(1), 2)
                    swir.write(sw3_band.read(1), 3)

                gcs_client.put(basedir + '/swir_temp.tiff',
                                "gs://gxiba/merged/SENTINEL/{}/{}_swir.tiff".format(self.id, self.id))

                main_pg_handler.execute(change_status_by_id.format(self.platform.lower(), 'Merged', self.id))

        else:
            pass

    def output(self):
        yield GCSTarget(path="gs://gxiba/merged/SENTINEL/{id}/{id}_rgb.tiff".format(**{'id': self.id}),
                         format=luigi.format.Nop,
                         client=gcs_client)
        yield GCSTarget(path="gs://gxiba/merged/SENTINEL/{id}/{id}_swir.tiff".format(**{'id': self.id}),
                         format=luigi.format.Nop,
                         client=gcs_client)


class ImageQuery (luigi.Task):
    platform = luigi.Parameter()

    def requires(self):
        pass

    def run(self):
        len_=100000
        while len_ > 0:
            row = main_pg_handler.fetch(get_one_by_status.format(self.platform.lower(), 'SYNCED'))
            print(row)
            yield ImageMerge(id=row[0][0], platform=self.platform)
            len_ = main_pg_handler.fetch(get_count_by_status.format(self.platform.lower(), 'SYNCED'))

    def output(self):
        pass