from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import Iterable

from sqlalchemy import Column, Text, DateTime, Numeric, update
from sqlalchemy.orm import registry

import gxiba.bigquery as gxiba_bigquery
import gxiba.data_objects.definitions as definitions

mapper_registry = registry()


@mapper_registry.mapped
@dataclass
class GxibaImageMetadata:
    __tablename__ = "gxiba_image_metadata"
    __table_args__ = {"schema": "gxiba"}
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
        engine.session.execute(update(GxibaImageMetadata).where(GxibaImageMetadata.platform_id == self.platform_id),
                               [self.as_dict])
        engine.session.commit()


def database_get_from_point(engine, latitude: float, longitude: float,
                            platform: definitions.SatelliteImagePlatform = None,
                            from_date: datetime = None, to_date: datetime = None,
                            status: str = None) -> Iterable[GxibaImageMetadata]:
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
    query_result = query_result.order_by(GxibaImageMetadata.sensing_time.asc())
    for row in query_result:
        yield row


def database_get_from_platform_id(platform_id, engine) -> GxibaImageMetadata | None:
    query_result = engine.session.query(GxibaImageMetadata).filter(GxibaImageMetadata.platform_id == platform_id)
    if (query_count := query_result.count()) > 1:
        raise Exception('Duplicate values in database.')
    if query_count < 1:
        return None
    return query_result.first()


def database_get_latest_by_platform(platform: str, engine) -> GxibaImageMetadata | None:
    query_result = engine.session.query(GxibaImageMetadata).filter(GxibaImageMetadata.platform == platform).order_by(
        GxibaImageMetadata.sensing_time.desc()).limit(1)
    return query_result.first()


def big_query_get_by_point(bigquery_interface: gxiba_bigquery.BigQueryInterface, engine,
                           platform: definitions.SatelliteImagePlatform, latitude: float, longitude: float,
                           from_date: datetime = None,
                           to_date: datetime = None) -> Iterable[GxibaImageMetadata]:
    query_constructor_buffer = "SELECT " + ', '.join(
        [f'{platform.database_mapping[member]} as {member}' for member in
         platform.database_mapping.keys()]) + \
                               f", \"{definitions.ImageProcessingStatus.BigQueryImport.name}\" as status" \
                               f" FROM {platform.big_query_path}" \
                               f" WHERE {platform.database_mapping['latitude_north']} >= {latitude}" \
                               f" AND {platform.database_mapping['latitude_south']} <= {latitude}" \
                               f" AND {platform.database_mapping['longitude_east']} >= {longitude}" \
                               f" AND {platform.database_mapping['longitude_west']} <= {longitude}"
    if from_date is not None:
        query_constructor_buffer += f""" AND sensing_time > '{from_date}'"""
    if to_date is not None:
        query_constructor_buffer += f""" AND sensing_time < '{to_date}'"""
    query_constructor_buffer += """ ORDER BY sensing_time ASC"""
    something = bigquery_interface.query(query_constructor_buffer)
    total_rows = something.result().total_rows
    for row in something:
        yield GxibaImageMetadata(*row), total_rows
