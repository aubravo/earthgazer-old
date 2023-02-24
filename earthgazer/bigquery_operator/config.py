import enum
import json
import re

from pydantic import BaseSettings, Json, FilePath, Field

from earthgazer.local_environment import LOCAL_PROJECT_PATH


class PlatformPaths(enum.Enum):
    SENTINEL_2 = "bigquery-public-data.cloud_storage_geo_index.sentinel_2_index"
    LANDSAT = "bigquery-public-data.cloud_storage_geo_index.landsat_index"


class PlatformMappings(enum.Enum):
    LANDSAT = {
        'platform_id': 'product_id',
        'platform': 'spacecraft_id',
        'sensing_time': 'sensing_time',
        'latitude_north': 'north_lat',
        'latitude_south': 'south_lat',
        'longitude_west': 'west_lon',
        'longitude_east': 'east_lon',
        'base_url': 'base_url'
    }
    SENTINEL_2 = {
        'platform_id': 'product_id',
        'platform': '"SENTINEL_2"',
        'sensing_time': 'sensing_time',
        'latitude_north': 'north_lat',
        'latitude_south': 'south_lat',
        'longitude_west': 'west_lon',
        'longitude_east': 'east_lon',
        'base_url': 'base_url'
    }


class PlatformParsing(enum.Enum):
    SENTINEL_2 = r'[\w/]+' \
                 r'(?P<mission_id>S[12AB]{2})_' \
                 r'(?P<product_level>MSIL\w{2})_' \
                 r'(?P<acquisition_timestamp>\d{8}T\d{6})_' \
                 r'(?P<pdgs_processing_baseline_number>N\d{4})_' \
                 r'(?P<relative_orbit_number>R\d{3})_' \
                 r'(?P<tile_number>T\w{5})_' \
                 r'(?P<product_discriminator_timestamp>\d{8}T\d{6}).SAFE/[\w/0]+' \
                 r'(?P<band>B\w{2}).jp2'
    LANDSAT = r'L(?P<sensor>[a-zA-Z])' \
              r'(?P<satellite>\d{2})_' \
              r'(?P<level>\w{4})_' \
              r'(?P<wrs_path>\d{3})' \
              r'(?P<wrs_row>\d{3})_' \
              r'(?P<acquisition_date>\d{8})_' \
              r'(?P<processing_date>\d{8})_' \
              r'(?P<collection_number>\d{2})_' \
              r'(?P<collection_category>[A-Z]\w)_' \
              r'(?P<band>B\d{1,2}).TIF'

    @property
    def compiled_regex(self):
        return re.compile(self.value)


class Platform(enum.Enum):
    SENTINEL_2 = "SENTINEL_2"
    LANDSAT = "LANDSAT"

    @enum.property
    def bigquery_path(self):
        return PlatformPaths[self.value].value

    @enum.property
    def database_mapping(self):
        return PlatformMappings[self.value].value

    @enum.property
    def band_metadata_parser(self):
        return PlatformParsing[self.value].compiled_regex


class Configuration(BaseSettings):
    service_account_credentials_path: FilePath = f'{LOCAL_PROJECT_PATH}\\keys.json'
    service_account_credentials: Json = Field(exclude=True)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not self.service_account_credentials:
            self.get_credentials_from_path()

    def get_credentials_from_path(self):
        with open(self.service_account_credentials_path) as credentials_path:
            self.service_account_credentials = json.load(credentials_path)
