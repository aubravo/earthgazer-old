import argparse
import datetime
import json
import logging
import sys
from pathlib import Path

try:
    import gxiba
    from gxiba.logger import setup_logger
except ModuleNotFoundError:
    root_path = Path(__file__).parents[1]
    sys.path.append(str(root_path))
    import gxiba
    from gxiba.logger import setup_logger

POPOCATEPETL_CRATER_LATITUDE = 19.023370
POPOCATEPETL_CRATER_LONGITUDE = -98.622864

parser = argparse.ArgumentParser(prog='gxibaUpdateFiles',
                                 description='Look at image metadata sources and update buckets and project '
                                             'database with new data.')
parser.add_argument('--skip-sentinel', action='store_false')
parser.add_argument('--skip-landsat', action='store_false')
parser.add_argument('-v', '--verbose', action='store_true', help='Set logging message level to Debug.')
parser.add_argument('-k', '--db-kind', help='Set database kind.', default='sqlite')
parser.add_argument('-H', '--db-host', help='Set database host.')
parser.add_argument('-U', '--db-username', help='Set database username.')
parser.add_argument('-P', '--db-password', help='Set database password.')
parser.add_argument('-p', '--db-port', help='Set database port.')
parser.add_argument('-d', '--db-name', help='Name of the database to use.', default='gxiba')
parser.add_argument('-F', '--force-engine', action='store_true', help='Force engine generation.')
parser.add_argument('-K', '--get-keys-from-env', action='store_true',
                    help='Get the Google Service Account keys from environmental variables instead of a keys.json file '
                         'stored in the project path.')
parser.add_argument('-B', '--bucket-path', help='Path to bucket.')


# Download command:
# gcs_client.download(f'gs://{gcs_client.interface.source_bucket.name}/{name}',
# f'C:/Users/alvaro.bravo/.gxiba/{x.platform_id}/{name.split("/")[-1]}')


if __name__ == "__main__":
    cli_arguments = parser.parse_args()
    setup_logger()
    logger = logging.getLogger()
    logger.debug('Logger set up.')

    # Setup logger
    if cli_arguments.verbose:
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.INFO)

    # Setup local storage
    local_storage = gxiba.LocalStorageManager()

    # Get keys
    if cli_arguments.get_keys_from_env:
        import os

        google_keys = json.loads(os.getenv('GOOGLE_KEYS'))
    else:
        with open(f'{local_storage.project_path}keys.json') as keys:
            google_keys = json.loads(keys.read())

    if cli_arguments.db_kind == 'sqlite':
        cli_arguments.db_name = str(Path(__file__).parents[1]) + f'\\{cli_arguments.db_name}.db'

    # Setup required interfaces
    bq_interface = gxiba.BigQueryInterface(google_keys)
    db_interface = gxiba.DataBaseInterface(database_kind=cli_arguments.db_kind,
                                           username=cli_arguments.db_username,
                                           password=cli_arguments.db_password,
                                           host=cli_arguments.db_host,
                                           port=cli_arguments.db_port,
                                           database=cli_arguments.db_name,
                                           echo=False,
                                           force_engine_generation=cli_arguments.force_engine)
    gcs_client = gxiba.CloudStorageManager(gxiba.GoogleCloudStorageInterface, google_keys)

    # Get latest images in project database
    if cli_arguments.skip_landsat:
        try:
            landsat_latest = gxiba.database_get_latest_by_platform(gxiba.SatelliteImagePlatform.LANDSAT_8.name,
                                                                   engine=db_interface).sensing_time
        except AttributeError:
            landsat_latest = datetime.datetime.min

        for count, (image_metadata, total_rows) in enumerate(
                gxiba.big_query_get_by_point(bq_interface, db_interface,
                                             platform=gxiba.SatelliteImagePlatform.LANDSAT_8,
                                             longitude=POPOCATEPETL_CRATER_LONGITUDE,
                                             latitude=POPOCATEPETL_CRATER_LATITUDE,
                                             from_date=landsat_latest)):
            logger.debug(f'Adding {image_metadata.platform_id} from LANDSAT to Database [{count + 1}/{total_rows}]')
            image_metadata.status = gxiba.ImageProcessingStatus.BigQueryImport.name
            db_interface.add(image_metadata)

    if cli_arguments.skip_sentinel:
        try:
            sentinel_latest = gxiba.database_get_latest_by_platform(gxiba.SatelliteImagePlatform.SENTINEL_2.name,
                                                                    engine=db_interface).sensing_time
        except AttributeError:
            sentinel_latest = datetime.datetime.min

        for count, (image_metadata, total_rows) in enumerate(
                gxiba.big_query_get_by_point(bq_interface, db_interface,
                                             platform=gxiba.SatelliteImagePlatform.SENTINEL_2,
                                             longitude=POPOCATEPETL_CRATER_LONGITUDE,
                                             latitude=POPOCATEPETL_CRATER_LATITUDE,
                                             from_date=sentinel_latest)):
            logger.debug(f'Adding {image_metadata.platform_id} from SENTINEL to Database [{count+1}/{total_rows}]')
            image_metadata.status = gxiba.ImageProcessingStatus.BigQueryImport.name
            db_interface.add(image_metadata)

    if cli_arguments.bucket_path is not None:
        # Get all not yet copied images
        if cli_arguments.skip_sentinel and cli_arguments.skip_landsat:
            gxiba_images = gxiba.database_get_from_point(
                db_interface, POPOCATEPETL_CRATER_LATITUDE, POPOCATEPETL_CRATER_LONGITUDE,
                status=gxiba.ImageProcessingStatus.BigQueryImport.name)
        elif cli_arguments.skip_sentinel:
            gxiba_images = gxiba.database_get_from_point(
                db_interface, POPOCATEPETL_CRATER_LATITUDE, POPOCATEPETL_CRATER_LONGITUDE,
                platform=gxiba.SatelliteImagePlatform.SENTINEL_2,
                status=gxiba.ImageProcessingStatus.BigQueryImport.name)
        elif cli_arguments.skip_landsat:
            gxiba_images = gxiba.database_get_from_point(
                db_interface, POPOCATEPETL_CRATER_LATITUDE, POPOCATEPETL_CRATER_LONGITUDE,
                platform=gxiba.SatelliteImagePlatform.LANDSAT_8,
                status=gxiba.ImageProcessingStatus.BigQueryImport.name)
        else:
            gxiba_images = []

        # Copy all images to prepare for processing
        for image_metadata in gxiba_images:
            logger.info(f'STARTING download of {image_metadata.platform_id} images.')
            blobs = gcs_client.list(image_metadata.base_url)
            for name in blobs:
                try:
                    if name[-4:] in ['.jp2'] and any(folder in name for folder in ['IMG_DATA']):
                        gcs_client.copy(f'gs://{gcs_client.interface.source_bucket.name}/{name}',
                                        f'gs://{cli_arguments.bucket_path}/{image_metadata.platform_id}/{name.split("/")[-1]}')
                    elif name[-4:] in ['.TIF']:
                        gcs_client.copy(f'gs://{gcs_client.interface.source_bucket.name}/{name}',
                                        f'gs://{cli_arguments.bucket_path}/{image_metadata.platform_id}/{name.split("/")[-1]}')
                except Exception as e:
                    raise Exception(e)
            image_metadata.status = gxiba.ImageProcessingStatus.ProjectStorage.name
            logger.info(f'{image_metadata.platform_id} status changed to {image_metadata.status}')
            image_metadata.update(db_interface)
