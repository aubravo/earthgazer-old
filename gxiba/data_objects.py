# included libraries
from collections.abc import Iterable, Generator
from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum

# 3rd party libraries
from sqlalchemy import Column, Numeric, Text, DateTime, update
from sqlalchemy.orm import registry

from gxiba.bigquery import BigQueryInterface

mapper_registry = registry()


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
    ImageProcessed = 3

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


@mapper_registry.mapped
@dataclass
class GxibaImageMetadata:
    __tablename__ = "gxiba_image_metadata"
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
    create_timestamp: datetime = field(default_factory=datetime.now, metadata={"sa": Column(DateTime)})
    last_update_timestamp: datetime = field(default_factory=datetime.now, metadata={"sa": Column(DateTime)})

    @property
    def as_dict(self) -> dict:
        return asdict(self)

    def update(self, engine):
        self.last_update_timestamp = datetime.now()
        print(self.as_dict)
        engine.session.execute(update(GxibaImageMetadata).where(GxibaImageMetadata.platform_id == self.platform_id),
                               [self.as_dict])
        engine.session.commit()


def big_query_get_by_point(bigquery_interface: BigQueryInterface, engine,
                           platform: SatelliteImagePlatform, latitude: float, longitude: float,
                           from_date: datetime = None,
                           to_date: datetime = None) -> Iterable[GxibaImageMetadata]:
    query_constructor_buffer = "SELECT " + ', '.join(
        [f'{platform.database_mapping[member]} as {member}' for member in
         platform.database_mapping.keys()]) + f", \"{ImageProcessingStatus.BigQueryImport.name}\" as status" \
                                              f" FROM {platform.big_query_path}" \
                                              f" WHERE {platform.database_mapping['latitude_north']} >= {latitude}" \
                                              f" AND {platform.database_mapping['latitude_south']} <= {latitude}" \
                                              f" AND {platform.database_mapping['longitude_east']} >= {longitude}" \
                                              f" AND {platform.database_mapping['longitude_west']} <= {longitude}"
    if from_date is not None:
        query_constructor_buffer += f""" AND sensing_time > '{from_date}'"""
    if to_date is not None:
        query_constructor_buffer += f""" AND sensing_time < '{to_date}'"""
    for row in bigquery_interface.query(query_constructor_buffer):
        yield GxibaImageMetadata(*row)


def database_get_from_platform_id(platform_id, engine) -> GxibaImageMetadata | None:
    query_result = engine.session.query(GxibaImageMetadata).filter(GxibaImageMetadata.platform_id == platform_id)
    if (query_count := query_result.count()) > 1:
        raise Exception('Duplicate values in database.')
    if query_count < 1:
        return None
    return query_result.first()


def database_get_from_point(engine, latitude: float, longitude: float, platform: SatelliteImagePlatform = None,
                            from_date: datetime = None, to_date: datetime = None,
                            status: str = None) -> Generator[GxibaImageMetadata] | Iterable[GxibaImageMetadata]:
    query_result = engine.session. \
        query(GxibaImageMetadata). \
        filter(GxibaImageMetadata.latitude_north >= latitude,
               GxibaImageMetadata.latitude_south <= latitude,
               GxibaImageMetadata.longitude_east >= longitude,
               GxibaImageMetadata.longitude_west <= longitude)
    if platform is not None:
        query_result = query_result.filter(GxibaImageMetadata.platform.like(f'%{platform.value}%'))
    if status is not None:
        query_result = query_result.filter(GxibaImageMetadata.status.like(f'%{status}%'))
    if from_date is not None:
        query_result = query_result.filter(GxibaImageMetadata.sensing_time >= from_date)
    if to_date is not None:
        query_result = query_result.filter(GxibaImageMetadata.sensing_time <= to_date)
    for row in query_result:
        yield row
