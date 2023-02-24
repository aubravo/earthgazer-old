"""GXIBA ENVIRONMENT

This code  is the heart of the gxiba project. Invoking or calling this script will attempt to generate the required
local environment as well as establish the necessary connections to services required by the project to run
successfully. Because of this, the gxiba.environment.py script is always imported first in any gxiba dependent files,
 as it will both provide the requirement configuration parameters either through variables for the most commonly used
parameters, or making them accessible through it's gxiba_config dictionary.

The previously mentioned parameters can be introduced into the project via environmental variables or the
.gxiba/gxiba.cfg file created upon the projects first run which is set up for running locally as default.
"""

import configparser
import datetime
import json
import logging
import os
import tempfile
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Callable

import sqlalchemy.exc
from sqlalchemy import create_engine, Column, Text, DateTime, Numeric, asc, desc
from sqlalchemy.engine import URL
from sqlalchemy.orm import scoped_session, sessionmaker, registry

import gxiba.data_sources.bigquery
import gxiba.drivers.cloud_storage_drivers


GXIBA_LIB_PATH = f'{Path(__file__).parents[2].absolute()}'
print(GXIBA_LIB_PATH)
GXIBA_PROJECT_PATH = os.getenv('GXIBA_PATH', f'{os.path.expanduser("~")}/.gxiba')
GXIBA_CONFIG_PATH = f'{GXIBA_PROJECT_PATH}/gxiba.cfg'


class GxibaPlaceholder:
    """This is placeholder class is used to handle non-existing connections to services. This can happen when one of
    these services is not configured correctly or when this services Active attribute is set as False in the
    gxiba.cfg file."""

    class NotInitializedError(Exception):
        ...

    def __init__(self, name):
        self._name = name

    def __getattr__(self, _item):
        raise self.NotInitializedError(f"{self._name} needs to be activated before usage."
                                       f"Please review your gxiba.cfg file or environmental variables.")

    def __call__(self, *args, **kwargs):
        raise self.NotInitializedError(f"{self._name} needs to be activated before usage."
                                       f"Please review your gxiba.cfg file or environmental variables.")


logging.basicConfig(level=logging.DEBUG,
                    format='{asctime}-{levelname:.<9}.{name:.<25}..{message}',
                    datefmt='%Y-%m-%dictionary %H:%M:%S',
                    style='{')

logger = logging.getLogger(__name__)

# =====================================================
# =======================Logger========================
# =====================================================

logger.debug('Setting up logger file handler.')
_log_file_name = datetime.datetime.now().strftime(gxiba_config['logs']['log_filename'])
file_handler = logging.FileHandler(f'{GXIBA_PROJECT_PATH}/log/{_log_file_name}')
file_handler.setLevel(gxiba_config['logs']['file_log_level'])
formatter = logging.Formatter(gxiba_config['logs']['log_format'],
                              style=gxiba_config['logs']['log_style'])
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)
logger.debug(f'...Saving logs under {GXIBA_PROJECT_PATH}/logs/{_log_file_name}')
logger.debug('File logging set up successfully.')

# =====================================================
# ======================Database=======================
# =====================================================

logger.debug('Creating database engine.')
GXIBA_DATABASE_ENGINE = create_engine(
    URL.create(drivername=gxiba_config['database']['drivername'],
               username=gxiba_config['database']['username'],
               password=gxiba_config['database']['password'],
               host=gxiba_config['database']['host'],
               port=gxiba_config['database']['port'],
               database=gxiba_config['database']['database']),
    echo=gxiba_config['database']['echo_sql'],
    future=True)

logger.debug(f'...Database engine created: {GXIBA_DATABASE_ENGINE}')
logger.debug(f'......Host: {gxiba_config["database"]["host"]}:{gxiba_config["database"]["port"]}')
logger.debug(f'......Username: {gxiba_config["database"]["username"]}')
logger.debug(f'......Database: {gxiba_config["database"]["database"]}')

logger.debug(f'Starting database session.')
session_factory = sessionmaker(bind=GXIBA_DATABASE_ENGINE)
GXIBA_DATABASE_SESSION = scoped_session(session_factory)
GXIBA_DATABASE_SCHEMA = gxiba_config['database']['schema']

logger.debug(f'...Attempting to create database structure.')
MAPPER_REGISTRY = registry()


class GxibaDataBaseObject:
    _in_database: bool
    create_timestamp: datetime
    last_update_timestamp: datetime

    def update(self):
        try:
            with GXIBA_DATABASE_SESSION() as threaded_session:
                if not self._in_database:
                    try:
                        self.create_timestamp = datetime.datetime.now()
                        self.last_update_timestamp = datetime.datetime.now()
                        threaded_session.add(self)
                        threaded_session.commit()
                        self._in_database = True
                    except sqlalchemy.exc.IntegrityError:
                        if 'ignore' in gxiba_config['database']['handle_duplicates'].lower():
                            threaded_session.rollback()
                            logger.debug('......Ignoring database record duplicate value')
                        else:
                            threaded_session.rollback()
                            raise
                else:
                    self.last_update_timestamp = datetime.datetime.now()
                    threaded_session.commit()
        except:
            logger.exception('Unable to handle database processes.')

    @property
    def as_dict(self) -> dict:
        return asdict(self)


@MAPPER_REGISTRY.mapped
@dataclass
class BandMetadata(GxibaDataBaseObject):
    __tablename__ = "band_metadata"
    if 'sqlite' not in GXIBA_DATABASE_ENGINE.name.lower():
        __table_args__ = {"schema": GXIBA_DATABASE_SCHEMA}
    __sa_dataclass_metadata_key__ = "sa"

    platform_id: str = field(metadata={"sa": Column(Text, primary_key=True)})
    band: int = field(metadata={"sa": Column(Text, primary_key=True)})
    metadata_field_name: str = field(metadata={"sa": Column(Text, primary_key=True)})
    metadata_field_value: str = field(metadata={"sa": Column(Text)})
    create_timestamp: datetime = field(default_factory=datetime.datetime.now, metadata={"sa": Column(DateTime)})
    last_update_timestamp: datetime = field(default_factory=datetime.datetime.now, metadata={"sa": Column(DateTime)})
    _in_database: bool = False

    def __post_init__(self):
        self._in_database = False


@MAPPER_REGISTRY.mapped
@dataclass
class ImageMetadata(GxibaDataBaseObject):
    __tablename__ = "image_metadata"
    if 'sqlite' not in GXIBA_DATABASE_ENGINE.name.lower():
        __table_args__ = {"schema": GXIBA_DATABASE_SCHEMA}
    __sa_dataclass_metadata_key__ = "sa"

    platform_id: str = field(metadata={"sa": Column(Text, primary_key=True)})
    platform: str = field(metadata={"sa": Column(Text)})
    sensing_time: datetime = field(metadata={"sa": Column(DateTime)})
    latitude_north: float = field(metadata={"sa": Column(Numeric)})
    latitude_south: float = field(metadata={"sa": Column(Numeric)})
    longitude_west: float = field(metadata={"sa": Column(Numeric)})
    longitude_east: float = field(metadata={"sa": Column(Numeric)})
    base_url: str = field(metadata={"sa": Column(Text)})
    status: str = field(metadata={"sa": Column(Text)})
    usage: str = field(default='', metadata={"sa": Column(Text)})
    create_timestamp: datetime = field(default_factory=datetime.datetime.now, metadata={"sa": Column(DateTime)})
    last_update_timestamp: datetime = field(default_factory=datetime.datetime.now, metadata={"sa": Column(DateTime)})
    _in_database: bool = False

    def __post_init__(self):
        self._in_database = False


MAPPER_REGISTRY.metadata.create_all(bind=GXIBA_DATABASE_ENGINE, checkfirst=True)


# ================Interaction Methods==================
def database_query(database_object, query_filters=None, order_by_parameter=None, order='asc'):
    if query_filters is None:
        query_filters = []
    threaded_session = GXIBA_DATABASE_SESSION()
    query = threaded_session.query(database_object)
    for query_filter in query_filters:
        query = query.filter(query_filter)
    if order_by_parameter:
        if order.lower() == 'asc':
            query = query.order_by(asc(order_by_parameter))
        elif order.lower() == 'desc':
            query = query.order_by(desc(order_by_parameter))
        else:
            raise NotImplementedError
    for result in query:
        result._in_database = True
        yield result


# =====================================================
# ======================BigQuery=======================
# =====================================================

# TODO: think of a way to introduce a sensible default for replacing BigQuery an allow for local testing.


GXIBA_BIGQUERY_INTERFACE: \
    gxiba.data_sources.bigquery.BigQueryInterface = GxibaPlaceholder(name='GXIBA_BIGQUERY_INTERFACE')
if gxiba_config['bigquery']['activate']:
    if unique_service_account_keys_location:
        bigquery_interface_keys_location = unique_service_account_keys_location
    else:
        bigquery_interface_keys_location = gxiba_config['bigquery']['service_account_keys_location']
    with open(bigquery_interface_keys_location) as service_account_keys:
        keys = json.load(service_account_keys)
    GXIBA_BIGQUERY_INTERFACE = gxiba.data_sources.bigquery.BigQueryInterface(keys)
    del bigquery_interface_keys_location

logger.info('Project environment setup complete!')


# =====================================================
# ===================Cloud Storage=====================
# =====================================================


class CloudStorageInterface:
    def __init__(self, driver: Callable, credentials: dict = None):
        if credentials is None:
            credentials = {}
        self._cloud_storage_interface = driver(credentials)

    @property
    def interface(self):
        return self._cloud_storage_interface

    def download(self, remote_path, local_path):
        self._cloud_storage_interface.download(remote_path, local_path)

    def upload(self, local_path, remote_path):
        self._cloud_storage_interface.upload(local_path, remote_path)

    def copy(self, source_path, destination_path):
        self._cloud_storage_interface.copy(source_path, destination_path)

    def list(self, remote_path):
        yield from self._cloud_storage_interface.list(remote_path)


# TODO: replace CloudStorageInterface default to LocalStorageInterface to allow for local testing.

GXIBA_CLOUD_STORAGE_INTERFACE: \
    CloudStorageInterface = GxibaPlaceholder(name='GXIBA_CLOUD_STORAGE_INTERFACE')

if gxiba_config['cloud-storage']['activate']:
    if unique_service_account_keys_location:
        cloud_storage_interface_keys_location = unique_service_account_keys_location
    else:
        cloud_storage_interface_keys_location = gxiba_config['cloud-storage']['service_account_keys_location']
    with open(cloud_storage_interface_keys_location) as service_account_keys:
        keys = json.load(service_account_keys)
    GXIBA_CLOUD_STORAGE_INTERFACE = CloudStorageInterface(
        driver=getattr(gxiba.drivers.cloud_storage_drivers, gxiba_config['cloud-storage']['driver']),
        credentials=keys
    )
    del cloud_storage_interface_keys_location

GXIBA_CLOUD_STORAGE_BUCKET = gxiba_config['cloud-storage']['bucket_name']

logger.info('Project environment setup complete!')

# Delete variables not available for user access
del GXIBA_LIB_PATH, gxiba_config_local, gxiba_config_types, gxiba_config_defaults, GXIBA_CONFIG_PATH
