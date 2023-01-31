import logging
import re
from datetime import datetime
from typing import Iterable

from sqlalchemy import DateTime, cast, func, DATE

from gxiba import BandMetadata, ImageMetadata

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


def database_get_landsat_band_metadata(engine, sensor: str = None, satellite: int = None, level: str = None,
                                       wrs_path: int = None, wrs_row: int = None, collection_number: int = None,
                                       collection_category: str = None, band: int = None,
                                       platform_id: str = None, status: str = None,
                                       acquisition_from_date: datetime = None, acquisition_to_date: datetime = None,
                                       processing_from_date: datetime = None, processing_to_date: datetime = None,
                                       order_by_asc: bool = True):
    query_result = engine.session.query(BandMetadata)
    if sensor:
        query_result = query_result.filter(BandMetadata.sensor.like(f'%{sensor}%'))
    # logger.debug(f'{query_result.count()} records found.')
    if satellite:
        query_result = query_result.filter(BandMetadata.satellite == satellite)
    # logger.debug(f'{query_result.count()} records found.')
    if level:
        query_result = query_result.filter(BandMetadata.level.like(f'%{level}%'))
    # logger.debug(f'{query_result.count()} records found.')
    if wrs_path:
        query_result = query_result.filter(BandMetadata.wrs_path == wrs_path)
    # logger.debug(f'{query_result.count()} records found.')
    if wrs_row:
        query_result = query_result.filter(BandMetadata.wrs_row == wrs_row)
    # logger.debug(f'{query_result.count()} records found.')
    if collection_number:
        query_result = query_result.filter(BandMetadata.collection_number == collection_number)
    # logger.debug(f'{query_result.count()} records found.')
    if collection_category:
        query_result = query_result.filter(BandMetadata.collection_category.like(f'%{collection_category}%'))
    # logger.debug(f'{query_result.count()} records found.')
    if band:
        query_result = query_result.filter(BandMetadata.band == band)
    # logger.debug(f'{query_result.count()} records found.')
    if platform_id:
        query_result = query_result.filter(BandMetadata.platform_id.like(f'%{platform_id}%'))
    # logger.debug(f'{query_result.count()} records found.')
    if status:
        query_result = query_result.filter(BandMetadata.status.like(f'%{status}%'))
    # logger.debug(f'{query_result.count()} records found.')
    if acquisition_from_date:
        query_result = query_result.filter(cast(
            func.concat(BandMetadata.acquisition_year, '-', BandMetadata.acquisition_month, '-',
                        BandMetadata.acquisition_day), DATE) >= acquisition_from_date.strftime('%Y-%m-%d'))
    # logger.debug(f'{query_result.count()} records found.')
    if acquisition_to_date:
        query_result = query_result.filter(cast(
            func.concat(BandMetadata.acquisition_year, '-', BandMetadata.acquisition_month, '-',
                        BandMetadata.acquisition_day), DATE) <= acquisition_to_date.strftime('%Y-%m-%d'))
    # logger.debug(f'{query_result.count()} records found.')
    if processing_from_date:
        query_result = query_result.filter(cast(
            func.concat(BandMetadata.processing_year, '-', BandMetadata.processing_month, '-',
                        BandMetadata.processing_day), DATE) >= processing_from_date.strftime('%Y-%m-%d'))
    # logger.debug(f'{query_result.count()} records found.')
    if processing_to_date:
        query_result = query_result.filter(cast(
            func.concat(BandMetadata.processing_year, '-', BandMetadata.processing_month, '-',
                        BandMetadata.processing_day), DATE) <= processing_to_date.strftime('%Y-%m-%d'))
    # logger.debug(f'{query_result.count()} records found.')
    if order_by_asc:
        query_result.order_by(cast(BandMetadata.acquisition_date, DateTime).asc())
    logger.debug(f'{query_result.count()} records found.')
    for result in query_result:
        yield result


def database_get_landsat_band_metadata_by_platform_id(engine, platform_id: str | ImageMetadata,
                                                      band: int = None) -> Iterable[BandMetadata]:
    if isinstance(platform_id, ImageMetadata):
        platform_id = platform_id.platform_id
    elif not isinstance(platform_id, str):
        raise NotImplementedError(f'Expected str or gxiba.GxibaImageMetadata, got {type(platform_id)} instead.')

    query_result = engine.session.query(BandMetadata). \
        filter(BandMetadata.platform_id.like(f'%{platform_id}%'))
    if band:
        query_result = query_result.filter(BandMetadata.band == band)
    for result in query_result:
        yield result


def create_landsat_band_metadata_from_file_name(file_name, platform_id: str,
                                                platform_url: str) -> BandMetadata | None:
    try:
        params = __name_parser(file_name)
    except AttributeError:
        return None
    if params is not None:
        params.update({'project_location_url': platform_url, 'platform_id': platform_id})
        return BandMetadata(**params)
    else:
        return None


def process_band_metadata(gxiba_image_metadata: ImageMetadata, database_interface, cloud_storage_manager,
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
