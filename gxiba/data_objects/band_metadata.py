import logging
import re
from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import Iterable

from sqlalchemy import Column, Text, DateTime, Numeric, update, cast, func, DATE

from gxiba.data_objects import mapper_registry
from gxiba.data_objects.image_metadata import GxibaImageMetadata

logger = logging.getLogger(__name__)

landsat_name_structure_parser = r'L(?P<sensor>[a-zA-Z])' \
                                r'(?P<satellite>\d{2})_' \
                                r'(?P<level>\w{4})_' \
                                r'(?P<wrs_path>\d{3})' \
                                r'(?P<wrs_row>\d{3})_' \
                                r'(?P<acquisition_year>\d{4})' \
                                r'(?P<acquisition_month>\d{2})' \
                                r'(?P<acquisition_day>\d{2})_' \
                                r'(?P<processing_year>\d{4})' \
                                r'(?P<processing_month>\d{2})' \
                                r'(?P<processing_day>\d{2})_' \
                                r'(?P<collection_number>\d{2})_' \
                                r'(?P<collection_category>[A-Z]\w)_B' \
                                r'(?P<band>\d{1,2}).TIF'

re_parser = name_parser = re.compile(landsat_name_structure_parser)


def __name_parser(file_name) -> dict | None:
    try:
        return re_parser.match(file_name).groupdict()
    except NotImplementedError:
        return None


@mapper_registry.mapped
@dataclass
class LandsatBandMetadata:
    __tablename__ = "landsat_band_metadata"
    __table_args__ = {"schema": "gxiba"}
    __sa_dataclass_metadata_key__ = "sa"

    sensor: str = field(metadata={"sa": Column(Text)})
    satellite: int = field(metadata={"sa": Column(Numeric)})
    level: str = field(metadata={"sa": Column(Text)})
    wrs_path: int = field(metadata={"sa": Column(Numeric)})
    wrs_row: int = field(metadata={"sa": Column(Numeric)})
    acquisition_year: int = field(metadata={"sa": Column(Numeric)})
    acquisition_month: int = field(metadata={"sa": Column(Numeric)})
    acquisition_day: int = field(metadata={"sa": Column(Numeric)})
    processing_year: int = field(metadata={"sa": Column(Numeric)})
    processing_month: int = field(metadata={"sa": Column(Numeric)})
    processing_day: int = field(metadata={"sa": Column(Numeric)})
    collection_number: int = field(metadata={"sa": Column(Numeric)})
    collection_category: str = field(metadata={"sa": Column(Text)})
    band: int = field(metadata={"sa": Column(Numeric, primary_key=True)})
    project_location_url: str = field(metadata={"sa": Column(Text)})
    platform_id: str = field(metadata={"sa": Column(Text, primary_key=True)})
    status: str = field(default='', metadata={"sa": Column(Text)})
    create_timestamp: datetime = field(default_factory=datetime.now, metadata={"sa": Column(DateTime)})
    last_update_timestamp: datetime = field(default_factory=datetime.now, metadata={"sa": Column(DateTime)})

    @property
    def as_dict(self) -> dict:
        return asdict(self)

    @property
    def processing_date(self) -> datetime:
        return datetime.fromisoformat(f'{self.processing_year}-{self.processing_month}-{self.processing_day}')

    @property
    def acquisition_date(self) -> datetime:
        return datetime.fromisoformat(f'{self.acquisition_year}-{self.acquisition_month}-{self.acquisition_day}')

    def update(self, engine):
        self.last_update_timestamp = datetime.now()
        engine.session.execute(update(LandsatBandMetadata).where(
            LandsatBandMetadata.platform_id == self.platform_id and LandsatBandMetadata.band == self.band),
            [self.as_dict])
        engine.session.commit()


def database_get_landsat_band_metadata(engine, sensor: str = None, satellite: int = None, level: str = None,
                                       wrs_path: int = None, wrs_row: int = None, collection_number: int = None,
                                       collection_category: str = None, band: int = None,
                                       platform_id: str = None, status: str = None,
                                       acquisition_from_date: datetime = None, acquisition_to_date: datetime = None,
                                       processing_from_date: datetime = None, processing_to_date: datetime = None,
                                       order_by_asc: bool = True):
    query_result = engine.session.query(LandsatBandMetadata)
    if sensor:
        query_result = query_result.filter(LandsatBandMetadata.sensor.like(f'%{sensor}%'))
    # logger.debug(f'{query_result.count()} records found.')
    if satellite:
        query_result = query_result.filter(LandsatBandMetadata.satellite == satellite)
    # logger.debug(f'{query_result.count()} records found.')
    if level:
        query_result = query_result.filter(LandsatBandMetadata.level.like(f'%{level}%'))
    # logger.debug(f'{query_result.count()} records found.')
    if wrs_path:
        query_result = query_result.filter(LandsatBandMetadata.wrs_path == wrs_path)
    # logger.debug(f'{query_result.count()} records found.')
    if wrs_row:
        query_result = query_result.filter(LandsatBandMetadata.wrs_row == wrs_row)
    # logger.debug(f'{query_result.count()} records found.')
    if collection_number:
        query_result = query_result.filter(LandsatBandMetadata.collection_number == collection_number)
    # logger.debug(f'{query_result.count()} records found.')
    if collection_category:
        query_result = query_result.filter(LandsatBandMetadata.collection_category.like(f'%{collection_category}%'))
    # logger.debug(f'{query_result.count()} records found.')
    if band:
        query_result = query_result.filter(LandsatBandMetadata.band == band)
    # logger.debug(f'{query_result.count()} records found.')
    if platform_id:
        query_result = query_result.filter(LandsatBandMetadata.platform_id.like(f'%{platform_id}%'))
    # logger.debug(f'{query_result.count()} records found.')
    if status:
        query_result = query_result.filter(LandsatBandMetadata.status.like(f'%{status}%'))
    # logger.debug(f'{query_result.count()} records found.')
    if acquisition_from_date:
        query_result = query_result.filter(cast(
            func.concat(LandsatBandMetadata.acquisition_year, '-', LandsatBandMetadata.acquisition_month, '-',
                        LandsatBandMetadata.acquisition_day), DATE) >= acquisition_from_date.strftime('%Y-%m-%d'))
    # logger.debug(f'{query_result.count()} records found.')
    if acquisition_to_date:
        query_result = query_result.filter(cast(
            func.concat(LandsatBandMetadata.acquisition_year, '-', LandsatBandMetadata.acquisition_month, '-',
                        LandsatBandMetadata.acquisition_day), DATE) <= acquisition_to_date.strftime('%Y-%m-%d'))
    # logger.debug(f'{query_result.count()} records found.')
    if processing_from_date:
        query_result = query_result.filter(cast(
            func.concat(LandsatBandMetadata.processing_year, '-', LandsatBandMetadata.processing_month, '-',
                        LandsatBandMetadata.processing_day), DATE) >= processing_from_date.strftime('%Y-%m-%d'))
    # logger.debug(f'{query_result.count()} records found.')
    if processing_to_date:
        query_result = query_result.filter(cast(
            func.concat(LandsatBandMetadata.processing_year, '-', LandsatBandMetadata.processing_month, '-',
                        LandsatBandMetadata.processing_day), DATE) <= processing_to_date.strftime('%Y-%m-%d'))
    # logger.debug(f'{query_result.count()} records found.')
    if order_by_asc:
        query_result.order_by(cast(LandsatBandMetadata.acquisition_date, DateTime).asc())
    logger.debug(f'{query_result.count()} records found.')
    for result in query_result:
        yield result


def database_get_landsat_band_metadata_by_platform_id(engine, platform_id: str | GxibaImageMetadata,
                                                      band: int = None) -> Iterable[LandsatBandMetadata]:
    if isinstance(platform_id, GxibaImageMetadata):
        platform_id = platform_id.platform_id
    elif not isinstance(platform_id, str):
        raise NotImplementedError(f'Expected str or gxiba.GxibaImageMetadata, got {type(platform_id)} instead.')

    query_result = engine.session.query(LandsatBandMetadata). \
        filter(LandsatBandMetadata.platform_id.like(f'%{platform_id}%'))
    if band:
        query_result = query_result.filter(LandsatBandMetadata.band == band)
    for result in query_result:
        yield result


def create_landsat_band_metadata_from_file_name(file_name, platform_id: str,
                                                platform_url: str) -> LandsatBandMetadata | None:
    try:
        params = __name_parser(file_name)
    except AttributeError:
        return None
    if params is not None:
        params.update({'project_location_url': platform_url, 'platform_id': platform_id})
        return LandsatBandMetadata(**params)
    else:
        return None


def process_band_metadata(gxiba_image_metadata: GxibaImageMetadata, database_interface, cloud_storage_manager,
                          bucket_path):
    if 'SENTINEL' in gxiba_image_metadata.platform:
        logger.debug('SENTINEL IMAGE')
        # TODO: Implement sentinel nameparser
        # labels: enhancement
        raise NotImplementedError
    elif 'LANDSAT' in gxiba_image_metadata.platform:
        logger.debug(f'{gxiba_image_metadata.platform_id} recognized as LandSat image.')
        for x in cloud_storage_manager.list(f'gs://{bucket_path}/{gxiba_image_metadata.platform_id}/'):
            band_name = x.split('/')[-1]
            logger.debug(f'Attempting to insert metadata from {gxiba_image_metadata.platform}:{band_name}')
            band_metadata = create_landsat_band_metadata_from_file_name(
                band_name, gxiba_image_metadata.platform_id,
                f'gs://{bucket_path}/{gxiba_image_metadata.platform_id}/{band_name}')
            if band_metadata is not None:
                band_metadata.status = 'MetadataInserted'
                database_interface.add(band_metadata)
                logger.debug(f'{band_metadata.platform_id} band {band_metadata.band} added to database.')
    else:
        raise NotImplementedError
