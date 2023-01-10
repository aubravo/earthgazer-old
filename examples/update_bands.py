import argparse
import json
import logging
from sqlalchemy import exc

import gxiba
from gxiba.logger import setup_logger
from gxiba.data_objects.band_metadata import create_from_file_name

parser = argparse.ArgumentParser(prog='gxibaUpdateFiles',
                                 description='Look at image metadata sources and update buckets and project '
                                             'database with new data.')
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
parser.add_argument('-i', '--platform-id', help='Platform id to download. If none provided uses latest.')
parser.add_argument('-B', '--bucket-path', help='Path to bucket.')
parser.add_argument('--skip-sentinel', action='store_true')
parser.add_argument('--skip-landsat', action='store_true')


def process_band_metadata(gxiba_image_metadata: gxiba.GxibaImageMetadata):
    if 'SENTINEL' in gxiba_image_metadata.platform:
        logger.debug('SENTINEL IMAGE')
        raise NotImplementedError
    elif 'LANDSAT' in gxiba_image_metadata.platform:
        logger.debug(f'{gxiba_image_metadata.platform_id} recognized as LandSat image.')
        for x in cloud_storage.list(f'gs://{cli_arguments.bucket_path}/{gxiba_image_metadata.platform_id}/'):
            band_name = x.split('/')[-1]
            logger.debug(f'Attempting to insert metadata from {gxiba_image_metadata.platform}:{band_name}')
            band_metadata = create_from_file_name(band_name, gxiba_image_metadata.platform_id, f'gs://{cli_arguments.bucket_path}/{gxiba_image_metadata.platform_id}/{band_name}')
            if band_metadata is not None:
                band_metadata.status = 'MetadataInserted'
                db_engine.add(band_metadata)
                logger.debug(f'{band_metadata.platform_id} band {band_metadata.band} added to database.')
    else:
        raise NotImplementedError


if __name__ == '__main__':
    cli_arguments = parser.parse_args()
    setup_logger()
    logger = logging.getLogger(__name__)
    logger.debug('Logger set up.')
    local_storage = gxiba.LocalStorageManager()
    with open(f'{local_storage.project_path}keys.json') as keys:
        google_keys = json.loads(keys.read())
    db_engine = gxiba.DataBaseEngine(database_kind=cli_arguments.db_kind,
                                     username=cli_arguments.db_username,
                                     password=cli_arguments.db_password,
                                     host=cli_arguments.db_host,
                                     port=cli_arguments.db_port,
                                     database=cli_arguments.db_name,
                                     echo=False,
                                     force_engine_generation=cli_arguments.force_engine)
    cloud_storage = gxiba.CloudStorageManager(gxiba.GoogleCloudStorageInterface, google_keys)
    if cli_arguments.platform_id is not None:
        process_band_metadata(gxiba.database_get_gxiba_image_metadata_from_platform_id(cli_arguments.platform_id, engine=db_engine))
        exit(0)
    else:
        if not cli_arguments.skip_sentinel:
            for image_band_metadata in gxiba.database_get_gxiba_image_metadata(db_engine, gxiba.SatelliteImagePlatform.SENTINEL_2, status=gxiba.ImageProcessingStatus.ProjectStorage):
                process_band_metadata(image_band_metadata)
                image_band_metadata.status = gxiba.ImageProcessingStatus.BandMetadataProcessed.name
                image_band_metadata.update(db_engine)
        if not cli_arguments.skip_landsat:
            for image_band_metadata in gxiba.database_get_gxiba_image_metadata(db_engine, gxiba.SatelliteImagePlatform.LANDSAT_8, status=gxiba.ImageProcessingStatus.ProjectStorage):
                process_band_metadata(image_band_metadata)
                image_band_metadata.status = gxiba.ImageProcessingStatus.BandMetadataProcessed.name
                image_band_metadata.update(db_engine)
