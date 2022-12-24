# included libraries
from datetime import datetime
from dataclasses import dataclass, field, asdict
from enum import Enum

# 3rd party libraries
from sqlalchemy import Column, Numeric, Text, DateTime, update
from sqlalchemy.orm import registry

mapper_registry = registry()


class SatelliteImagePlatform(Enum):
    SENTINEL2 = "Sentinel2"
    LANDSAT8 = "Landsat8"

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

    @staticmethod
    def get_from_platform_id(platform_id, engine):
        query_result = engine.session.query(GxibaImageMetadata).filter(GxibaImageMetadata.platform_id == platform_id)
        if (query_count := query_result.count()) > 1:
            raise Exception('Duplicate values in database.')
        if query_count < 1:
            raise Exception('Searched platform id not registered.')
        return query_result.first()

    @property
    def as_dict(self):
        return asdict(self)

    def update(self, engine):
        print(self.as_dict)
        engine.session.execute(update(GxibaImageMetadata).where(GxibaImageMetadata.platform_id == self.platform_id),
                               [self.as_dict])
