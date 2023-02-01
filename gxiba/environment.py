import configparser
import datetime
import json
import logging
import os
import tempfile
from dataclasses import asdict, dataclass, field
from pathlib import Path

import sqlalchemy.exc
from sqlalchemy import create_engine, Column, Text, Integer, DateTime, Numeric
from sqlalchemy.engine import URL
from sqlalchemy.orm import Session, registry

__version__ = '0.5.1'

import gxiba.data_sources.bigquery
import gxiba.drivers
import gxiba.cloud_storage


class GxibaPlaceholder:
    class NotInitializedError(Exception):
        ...

    def __init__(self, name):
        self._name = name

    def __getattr__(self, item):
        raise self.NotInitializedError(f"{self._name} needs to be activated before usage."
                                       f"Please review your gxiba.cfg file or environmental variables.")

    def __call__(self, *args, **kwargs):
        raise self.NotInitializedError(f"{self._name} needs to be activated before usage."
                                       f"Please review your gxiba.cfg file or environmental variables.")


logging.basicConfig(level=logging.DEBUG,
                    format='{asctime}-{levelname:.<9}.{name:.<25}..{message}', datefmt='%Y-%m-%d %H:%M:%S', style='{')

logger = logging.getLogger(__name__)

logger.info(f"""\n
                   ▄▄ • ▐▄• ▄ ▪  ▄▄▄▄·  ▄▄▄·
                  ▐█ ▀ ▪ █▌█▌▪██ ▐█ ▀█▪▐█ ▀█
                  ▄█ ▀█▄ ·██· ▐█·▐█▀▀█▄▄█▀▀█
                  ▐█▄▪▐█▪▐█·█▌▐█▌██▄▪▐█▐█▪ ▐▌
                  ·▀▀▀▀ •▀▀ ▀▀▀▀▀·▀▀▀▀  ▀  ▀ 
-----------------------------------------------------------------
Version {__version__}
Project homepage at: https://github.com/aubravo/gxiba
For more information contact: alvaroubravo@gmail.com
-----------------------------------------------------------------
""")


# =====================================================
# =============Project system structure================
# =====================================================


def path_builder(path: str):
    logger.debug(f'......Attempting to create path: {path}')
    Path(path).mkdir(parents=True, exist_ok=True)


# Get the library's installation path
_gxiba_lib_path = f'{Path(__file__).parents[1].absolute()}'
logger.debug(f'Gxiba lib installed in: {_gxiba_lib_path}')

# Local path construction starts here
logger.debug(f'Starting project environment definition.')
logger.debug(f'Following structure will be created if not present:')

# Main project path
GXIBA_PATH = os.getenv('GXIBA_PATH', f'{os.path.expanduser("~")}/.gxiba')
logger.debug(f'...Project base path: {GXIBA_PATH}')
path_builder(GXIBA_PATH)

# Sub structure creation and configuration
LOGGING_PATH = f'{GXIBA_PATH}/log'
logger.debug(f'...Log path: {LOGGING_PATH}')
path_builder(LOGGING_PATH)

TEMP_PATH = f'{GXIBA_PATH}/temp'
logger.debug(f'...Temp files path: {TEMP_PATH}')
path_builder(TEMP_PATH)
tempfile.tempdir = TEMP_PATH

logger.debug('Getting monitored locations file.')
GXIBA_LOCATIONS = {}
if os.path.exists(f'{GXIBA_PATH}/locations.json') and os.path.getsize(f'{GXIBA_PATH}/locations.json') > 0:
    with open(f'{GXIBA_PATH}/locations.json', 'r+') as locations:
        GXIBA_LOCATIONS = json.load(locations)['locations']
else:
    with open(f'{GXIBA_PATH}/locations.json', 'w+') as locations:
        ...

for location in GXIBA_LOCATIONS:
    for key in location.keys():
        logger.debug(f'...Found monitored location: {key} at {location[key]["latitude"]}, {location[key]["longitude"]}')

# =====================================================
# ===============Project configuration=================
# =====================================================
_gxiba_config_path = f'{GXIBA_PATH}/gxiba.cfg'


# Type mappers
def config_bool(value: str):
    if isinstance(value, str):
        if value.lower() in ("yes", "true", "1"):
            return True
        elif value == '':
            return None
    elif value is None:
        return None
    else:
        raise TypeError('value should be an instance of \'str\'.')


def config_int(value: str):
    if isinstance(value, str):
        if value == '':
            return None
        else:
            return int(value)
    elif value is None:
        return None
    else:
        raise TypeError('value should be an instance of \'str\'.')


def config_float(value: str):
    if isinstance(value, str):
        if value == '':
            return None
        else:
            return float(value)
    elif value is None:
        return None
    else:
        raise TypeError('value should be an instance of \'str\'.')


# Create config file in project path if it doesn't exist

logger.debug('Setting up project configuration parameters.')

if not os.path.exists(f'{GXIBA_PATH}/gxiba.cfg'):
    with open(f'{_gxiba_lib_path}/templates/gxiba.cfg', 'r') as gxiba_config_template, \
            open(_gxiba_config_path, 'w') as gxiba_config_file:
        for line in gxiba_config_template:
            if not line[:2] == '#!':
                gxiba_config_file.write(line)

# Read config values and replace them by corresponding environmental variable value if present

gxiba_config = {}
gxiba_config_local = configparser.ConfigParser()
gxiba_config_local.read(_gxiba_config_path)
gxiba_config_types = configparser.ConfigParser()
gxiba_config_types.read(f'{_gxiba_lib_path}/templates/gxiba_types.cfg')
gxiba_config_defaults = configparser.ConfigParser()
gxiba_config_defaults.read(f'{_gxiba_lib_path}/templates/gxiba.cfg')

for section in gxiba_config_defaults.sections():
    gxiba_config[section] = {}
    for item in gxiba_config_defaults[section]:
        if parameter := os.getenv(
                f'GXIBA__{str(section.upper().replace("-", "_"))}__{str(item).upper().replace("-", "_")}'):
            logger.debug(f'...Environment override found for parameter {section}.{item}')
            gxiba_config_local[section][item] = parameter
        try:
            parameter_value = gxiba_config_local[section][item]
        except KeyError:
            logger.debug(f'...No value found for parameter {section}.{item}. Setting to default.')
            parameter_value = gxiba_config_defaults[section][item]
        if gxiba_config_types[section][item] == 'string':
            gxiba_config[section].update({item: parameter_value})
        elif gxiba_config_types[section][item] == 'int':
            gxiba_config[section].update({item: config_int(parameter_value)})
        elif gxiba_config_types[section][item] == 'bool':
            gxiba_config[section].update({item: config_bool(parameter_value)})
        elif gxiba_config_types[section][item] == 'float':
            gxiba_config[section].update({item: config_float(parameter_value)})
        else:
            raise NotImplementedError(f'No type handling implemented for \'{gxiba_config_types[section][item]}\'')

gxiba_single_accoount_keys_location = gxiba_config['core']['service_account_keys_location']


# =====================================================
# =======================Logger========================
# =====================================================

logger.debug('Setting up logger file handler.')
_log_file_name = datetime.datetime.now().strftime(gxiba_config['logs']['log_filename'])
file_handler = logging.FileHandler(f'{GXIBA_PATH}/log/{_log_file_name}')
file_handler.setLevel(gxiba_config['logs']['file_log_level'])
formatter = logging.Formatter(gxiba_config['logs']['log_format'],
                              style=gxiba_config['logs']['log_style'])
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)
logger.debug(f'...Saving logs under {GXIBA_PATH}/logs/{_log_file_name}')
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
GXIBA_DATABASE_SESSION = Session(GXIBA_DATABASE_ENGINE)
GXIBA_DATABASE_SCHEMA = gxiba_config['database']['schema']


logger.debug(f'...Attempting to create database structure.')
MAPPER_REGISTRY = registry()


class GxibaDataBaseObject:

    _in_database: bool
    create_timestamp: datetime
    last_update_timestamp: datetime

    def update(self):
        if not self._in_database:
            try:
                self.create_timestamp = datetime.datetime.now()
                self.last_update_timestamp = datetime.datetime.now()
                GXIBA_DATABASE_SESSION.add(self)
                GXIBA_DATABASE_SESSION.commit()
                self._in_database = True
            except sqlalchemy.exc.IntegrityError:
                if 'overwrite' in gxiba_config['database']['handle_duplicates'].lower():
                    GXIBA_DATABASE_SESSION.rollback()
                    self.create_timestamp = datetime.datetime.now()
                    self.last_update_timestamp = datetime.datetime.now()
                    GXIBA_DATABASE_SESSION.commit()
                elif 'ignore' in gxiba_config['database']['handle_duplicates'].lower():
                    GXIBA_DATABASE_SESSION.rollback()
                    logger.debug('......Ignoring duplicate value')
                else:
                    raise

        else:
            self.last_update_timestamp = datetime.datetime.now()
            GXIBA_DATABASE_SESSION.commit()

    def drop(self):
        GXIBA_DATABASE_SESSION.delete(self)

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
    band: int = field(metadata={"sa": Column(Integer, primary_key=True)})
    metadata_field_name: str = field(metadata={"sa": Column(Text, primary_key=True)})
    metadata_field_value: str = field(metadata={"sa": Column(Text)})
    create_timestamp: datetime = field(default_factory=datetime.datetime.now, metadata={"sa": Column(DateTime)})
    last_update_timestamp: datetime = field(default_factory=datetime.datetime.now, metadata={"sa": Column(DateTime)})
    _in_database: bool = False

    def __post_init__(self):
        self._in_database = False


@ MAPPER_REGISTRY.mapped
@ dataclass
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


# =====================================================
# ======================BigQuery=======================
# =====================================================


GXIBA_BIGQUERY_INTERFACE: gxiba.data_sources.bigquery.BigQueryInterface = GxibaPlaceholder(
                                                                            name='GXIBA_BIGQUERY_INTERFACE')
if gxiba_config['bigquery']['activate']:
    if gxiba_single_accoount_keys_location:
        bigquery_interface_keys_location = gxiba_single_accoount_keys_location
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


GXIBA_CLOUD_STORAGE_INTERFACE: gxiba.cloud_storage.CloudStorageInterface = GxibaPlaceholder(
                                                                            name='GXIBA_CLOUD_STORAGE_INTERFACE')

if gxiba_config['cloud-storage']['activate']:
    if gxiba_single_accoount_keys_location:
        cloud_storage_interface_keys_location = gxiba_single_accoount_keys_location
    else:
        cloud_storage_interface_keys_location = gxiba_config['cloud-storage']['service_account_keys_location']
    with open(cloud_storage_interface_keys_location) as service_account_keys:
        keys = json.load(service_account_keys)
    GXIBA_CLOUD_STORAGE_INTERFACE = gxiba.cloud_storage.CloudStorageInterface(
        driver=getattr(gxiba.drivers, gxiba_config['cloud-storage']['driver']),
        credentials=keys
    )
    del cloud_storage_interface_keys_location

GXIBA_CLOUD_STORAGE_BUCKET = gxiba_config['cloud-storage']['bucket_name']

logger.info('Project environment setup complete!')

# Delete variables not available for user access
del _gxiba_lib_path, gxiba_config_local, gxiba_config_types, gxiba_config_defaults, _gxiba_config_path
