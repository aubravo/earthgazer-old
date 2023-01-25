import argparse
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
    local_storage = gxiba.LocalEnvironmentManager()

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
    db_interface = gxiba.DataBaseEngine(kind=cli_arguments.db_kind,
                                        username=cli_arguments.db_username,
                                        password=cli_arguments.db_password,
                                        host=cli_arguments.db_host,
                                        port=cli_arguments.db_port,
                                        database=cli_arguments.db_name,
                                        echo=False,
                                        force_engine_generation=cli_arguments.force_engine)
    # gcs_client = gxiba.CloudStorageManager(gxiba.GoogleCloudStorageInterface, google_keys)


