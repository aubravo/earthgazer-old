from enum import Enum


class BigQueryPath(Enum):
    SENTINEL_2 = "bigquery-public-data.cloud_storage_geo_index.sentinel_2_index"
    LANDSAT = "bigquery-public-data.cloud_storage_geo_index.landsat_index"


class SatelliteImagePlatform(Enum):
    SENTINEL_2 = "SENTINEL_2"
    LANDSAT_8 = "LANDSAT_8"
    LANDSAT_7 = "LANDSAT_7"
    LANDSAT_5 = "LANDSAT_5"
    LANDSAT_4 = "LANDSAT_4"
    __database_mapping__ = \
        {
            'landsat':
                {
                    'platform_id': 'product_id',
                    'platform': 'spacecraft_id',
                    'sensing_time': 'sensing_time',
                    'latitude_north': 'north_lat',
                    'latitude_south': 'south_lat',
                    'longitude_west': 'west_lon',
                    'longitude_east': 'east_lon',
                    'base_url': 'base_url'
                },
            'sentinel_2':
                {
                    'platform_id': 'product_id',
                    'platform': '"SENTINEL_2"',
                    'sensing_time': 'sensing_time',
                    'latitude_north': 'north_lat',
                    'latitude_south': 'south_lat',
                    'longitude_west': 'west_lon',
                    'longitude_east': 'east_lon',
                    'base_url': 'base_url'
                }
        }

    def __getitem__(self, item):
        return item

    @property
    def big_query_path(self):
        try:
            if 'LANDSAT' in self.name:
                return BigQueryPath.LANDSAT.value
            return BigQueryPath.__dict__.get(self.name).value
        except AttributeError:
            raise AttributeError(f"BigQueryPath has no attribute {self.name}.")

    @property
    def database_mapping(self):
        if 'SENTINEL_2' in self.name:
            return self.__database_mapping__['sentinel_2']
        elif 'LANDSAT' in self.name:
            return self.__database_mapping__['landsat']
        raise NotImplementedError

    def __eq__(self, other):
        if isinstance(other, str):
            return self.value == other
        if isinstance(other, SatelliteImagePlatform):
            return self is other
        return False

    def __str__(self):
        return f'{self.value}'


class ImageProcessingStatus(Enum):
    BigQueryImport = 1
    ProjectStorage = 2
    BandMetadataProcessed = 3

    def __eq__(self, other):
        if isinstance(other, str):
            return self.name == other
        if isinstance(other, int):
            return self.value == other
        if isinstance(other, ImageProcessingStatus):
            return self is other
        return False

    def __str__(self):
        return f'{self.name}'
