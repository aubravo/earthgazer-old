import argparse
import logging
from pathlib import Path
import json
from gxiba.logger import setup_logger
import gxiba


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
parser.add_argument('-B', '--bucket-path', help='Path to bucket.')


if __name__ == '__main__':
    cli_arguments = parser.parse_args()
    setup_logger()
    logger = logging.getLogger(__name__)
    logger.debug('Logger set up.')

    local_storage = gxiba.LocalStorageManager()
    with open(f'{local_storage.project_path}keys.json') as keys:
        google_keys = json.loads(keys.read())
    db_interface = gxiba.DataBaseInterface(database_kind=cli_arguments.db_kind,
                                           username=cli_arguments.db_username,
                                           password=cli_arguments.db_password,
                                           host=cli_arguments.db_host,
                                           port=cli_arguments.db_port,
                                           database=cli_arguments.db_name,
                                           echo=False,
                                           force_engine_generation=cli_arguments.force_engine)
    cloud_storage = gxiba.CloudStorageManager(gxiba.GoogleCloudStorageInterface, google_keys)

    landsat_latest = gxiba.database_get_latest_by_platform(gxiba.SatelliteImagePlatform.LANDSAT_8.name,
                                                           engine=db_interface)
    images = cloud_storage.list(f'gs://{cli_arguments.bucket_path}/{landsat_latest.platform_id}/')
    for item in images:
        logger.debug(item)
        Path(f'{local_storage.project_path}{item}').parents[0].mkdir(parents=True, exist_ok=True)
        cloud_storage.download(f'gs://{cli_arguments.bucket_path}/{item}', f'{local_storage.project_path}{item}')
