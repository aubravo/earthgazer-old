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
import numpy as np
from tifffile import imread, imwrite

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

landsat_bands = {"B2": 'blue',
                 "B3": 'green',
                 "B4": 'red',
                 "B5": 'swir1',
                 "B6": 'swir2',
                 "B7": 'swir3'}

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

    def requires(self):
        main_pg_handler.execute(change_status_by_id.format(self.platform.lower(), 'Processing', self.id))
        files = gcs_client.listdir("gs://gxiba/{platform}/{id}/".format(**{'platform': self.platform,
                                                                           'id': self.id}))
        image_bands = {}
        if self.platform == 'SENTINEL':
            band_list = sentinel_bands
        elif self.platform == 'LANDSAT':
            band_list = landsat_bands
        else:
            raise Exception('Platform not supported.')

        for filename in files:
            for band in band_list.keys():
                if band in filename:
                    image_bands[band_list[band]] = filename
                    break
        if len(image_bands.keys()) < len(band_list.values()):
            differences = ''
            for missing_band in list(set(band_list.values()) - set(image_bands.keys())):
                differences = differences + missing_band + ','
            main_pg_handler.execute(change_status_by_id.format(self.platform.lower(),
                                                               'Missing Bands: {}'.format(differences[:-1]),
                                                               self.id))
        else:
            return {band: GetImages(path=image_bands[band]) for band in image_bands.keys()}

    def run(self):
        params = {'platform': self.platform,
                  'id': self.id}
        with tempfile.TemporaryDirectory() as _dir:
            local_basedir = _dir.replace('\\', '/').replace('C:/', 'C://')
            remote_basedir = 'gs://gxiba/merged/{platform}/{id}'.format(**params)
            filename = '/{id}_{band_range}.tiff'
            if self.platform == 'SENTINEL':
                params['band_range'] = 'rgb'
                bands = ['red', 'green', 'blue']
                for band in bands:
                    with self.input()[band].open as remote_file,\
                            open(local_basedir + '/{}.jp2'.format(band),'wb')as local_file:
                        local_file.write(remote_file.read())

                with rasterio.open(local_basedir + '/r_temp.jp2', driver='JP2OpenJPEG') as r_band,\
                    rasterio.open(local_basedir + '/g_temp.jp2', driver='JP2OpenJPEG') as g_band,\
                    rasterio.open(local_basedir + '/b_temp.jp2', driver='JP2OpenJPEG') as b_band,\
                    rasterio.open(local_basedir + filename.format(**params), 'w+', driver='Gtiff',
                                  width=r_band.width, height=r_band.height, count=3, crs=r_band.crs,
                                  transform=r_band.transform, dtype='uint16') as rgb:
                    rgb.write(r_band.read(1), 1)
                    rgb.write(g_band.read(1), 2)
                    rgb.write(b_band.read(1), 3)

                gcs_client.put(local_basedir + filename.format(**params),
                               remote_basedir + filename.format(**params))

                with self.input()['swir1'].open() as sw1_gcs,\
                        self.input()['swir2'].open() as sw2_gcs,\
                        self.input()['swir3'].open() as sw3_gcs,\
                        open(local_basedir + "/sw1_temp.jp2", 'wb') as sw1_t,\
                        open(local_basedir + "/sw2_temp.jp2", 'wb') as sw2_t,\
                        open(local_basedir + "/sw3_temp.jp2", 'wb') as sw3_t:
                    sw1_t.write(sw1_gcs.read())
                    sw2_t.write(sw2_gcs.read())
                    sw3_t.write(sw3_gcs.read())

                with rasterio.open(local_basedir + '/sw1_temp.jp2', driver='JP2OpenJPEG') as sw1_band,\
                    rasterio.open(local_basedir + '/sw2_temp.jp2', driver='JP2OpenJPEG') as sw2_band,\
                    rasterio.open(local_basedir + '/sw3_temp.jp2', driver='JP2OpenJPEG') as sw3_band,\
                    rasterio.open(local_basedir + '/swir_temp.tiff', 'w+', driver='Gtiff', width=sw1_band.width,
                                  height=sw1_band.height, count=3, crs=sw1_band.crs, transform=sw1_band.transform,
                                  dtype='uint16') as swir:
                    swir.write(sw1_band.read(1), 1)
                    swir.write(sw2_band.read(1), 2)
                    swir.write(sw3_band.read(1), 3)

                gcs_client.put(local_basedir + '/swir_temp.tiff',
                                "gs://gxiba/merged/SENTINEL/{}/{}_swir.tiff".format(self.id, self.id))

                params['status'] = 'Merged'
                main_pg_handler.execute(change_status_by_id.format(**params))

            elif self.platform == 'LANDSAT':
                pass

    def output(self):
        yield GCSTarget(path="gs://gxiba/merged/{platform}/{id}/{id}_rgb.tiff".format(**{'id': self.id,
                                                                                         'platform': self.platform}),
                         format=luigi.format.Nop,
                         client=gcs_client)
        yield GCSTarget(path="gs://gxiba/merged/{platform}/{id}/{id}_swir.tiff".format(**{'id': self.id,
                                                                                          'platform': self.platform}),
                         format=luigi.format.Nop,
                         client=gcs_client)


class ImageQuery (luigi.Task):
    platform = luigi.Parameter()

    def requires(self):
        pass

    def run(self):
        params = {'platform': self.platform,
                  'status': 'SYNCED'}
        len_ = main_pg_handler.fetch(get_count_by_status.format(**params))
        while len_ > 0:
            id_ = main_pg_handler.fetch(get_one_by_status.format(**params))[0][0]
            yield ImageMerge(id=id_, platform=self.platform)
            len_ = main_pg_handler.fetch(get_count_by_status.format(**params))

    def output(self):
        pass