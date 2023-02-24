import concurrent.futures
import logging
import re
from datetime import datetime
from time import perf_counter
from typing import Iterable

import gxiba.environment

logger = logging.getLogger(__name__)


def get_image_metadata_from_big_query(platform: gxiba.SatelliteImagePlatform | str = None,
                                      latitude: float = None,
                                      longitude: float = None,
                                      from_date: datetime = None,
                                      to_date: datetime = None,
                                      order_asc: bool = True) -> Iterable[gxiba.ImageMetadata]:
    def iterate_over_platform(_platform):
        logger.debug('Starting create gxiba image metadata from big query process.')
        logger.debug(f'...Platform: {_platform}')
        logger.debug(f'...Latitude: {latitude if latitude else "Not defined"}')
        logger.debug(f'...Longitude: {longitude if longitude else "Not defined"}')
        logger.debug(f'...From date: {from_date if from_date else "Not defined"}')
        logger.debug(f'...To date: {to_date if to_date else "Not defined"}')

        query_constructor_buffer = "SELECT " + ',\n'.join(
            [f'{_platform.database_mapping[member]} as {member}' for member in _platform.database_mapping.keys()])
        query_constructor_buffer += f",\n\"{gxiba.ImageProcessingStatus.BigQueryImport.name}\" as status\n" \
                                    f"FROM {_platform.big_query_path}\n"
        queries = []
        if latitude:
            queries.append(
                f"{_platform.database_mapping['latitude_north']} >= {latitude} \n"
                f"AND {_platform.database_mapping['latitude_south']} <= {latitude}")
        if longitude:
            queries.append(
                f"{_platform.database_mapping['longitude_east']} >= {longitude} \n"
                f"AND {_platform.database_mapping['longitude_west']} <= {longitude}")
        if from_date:
            queries.append([f"""sensing_time > '{from_date}'"""])
        if to_date:
            queries.append([f"""sensing_time < '{to_date}'"""])

        if queries:
            query_constructor_buffer += f"WHERE " + '\nAND '.join([query for query in queries])

        if order_asc:
            query_constructor_buffer += """\nORDER BY sensing_time ASC"""

        formatted_query = '\n\t\t'.join([line for line in query_constructor_buffer.split('\n')])
        logger.debug(f'...Query result:\n\t\t{formatted_query}')

        for result in gxiba.GXIBA_BIGQUERY_INTERFACE.query(query_constructor_buffer):
            yield gxiba.ImageMetadata(*result)

    if platform:
        iterate_over_platform(platform)
    else:
        # yield from iterate_over_platform(gxiba.SatelliteImagePlatform.SENTINEL_2)
        yield from iterate_over_platform(gxiba.SatelliteImagePlatform.LANDSAT_8)


landsat_parser = re.compile(r'L(?P<sensor>[a-zA-Z])'
                            r'(?P<satellite>\d{2})_'
                            r'(?P<level>\w{4})_'
                            r'(?P<wrs_path>\d{3})'
                            r'(?P<wrs_row>\d{3})_'
                            r'(?P<acquisition_date>\d{8})_'
                            r'(?P<processing_date>\d{8})_'
                            r'(?P<collection_number>\d{2})_'
                            r'(?P<collection_category>[A-Z]\w)_'
                            r'(?P<band>B\d{1,2}).TIF')

sentinel_parser = re.compile(r'[\w/]+'
                             r'(?P<mission_id>S[12AB]{2})_'
                             r'(?P<product_level>MSIL\w{2})_'
                             r'(?P<acquisition_timestamp>\d{8}T\d{6})_'
                             r'(?P<pdgs_processing_baseline_number>N\d{4})_'
                             r'(?P<relative_orbit_number>R\d{3})_'
                             r'(?P<tile_number>T\w{5})_'
                             r'(?P<product_discriminator_timestamp>\d{8}T\d{6}).SAFE/[\w/0]+'
                             r'(?P<band>B\w{2}).jp2')


def process_image_metadata(image_metadata):
    try:
        logger.debug(f'...Adding: {image_metadata.platform_id} to Image Metadata table.')
        image_metadata.update()
        logger.info(f'...Beginning download of {image_metadata.platform_id} images.')
        blobs = gxiba.GXIBA_CLOUD_STORAGE_INTERFACE.list(image_metadata.base_url)
        for name in blobs:

            # TODO: Fix hardcoded gs bucket path.

            bucket_source_path = f'gs://{gxiba.GXIBA_CLOUD_STORAGE_INTERFACE.interface.source_bucket.name}/{name}'
            bucket_save_path = f'gs://{gxiba.GXIBA_CLOUD_STORAGE_BUCKET}/' \
                               f'{image_metadata.platform_id}/{name.split("/")[-1]}'

            logger.debug(f'......Attempting to copy file "{name}" to own bucket.')
            if name[-4:] in ['.jp2'] and any(folder in name for folder in ['IMG_DATA']):
                logger.debug(f'......Attempting to insert metadata from {image_metadata.platform_id}:{name}')
                platform_id = image_metadata.platform_id
                try:
                    params = sentinel_parser.match(name).groupdict()
                except AttributeError:
                    logger.debug(
                        f'......{image_metadata.platform_id}:{name} could not be inserted because it failed to parse.')
                    continue
                if params is not None:
                    params.update({
                        'project_location_url': bucket_save_path,
                        'platform_id': platform_id,
                        'status': 'BandMetadataProcessed'})
                    for band_metadata in params:
                        if band_metadata != 'band' and band_metadata != platform_id:
                            logger.debug(
                                f'...Adding {band_metadata} from {platform_id}, band {params["band"]} to database.')
                            gxiba.BandMetadata(
                                platform_id=platform_id,
                                band=params['band'],
                                metadata_field_name=band_metadata,
                                metadata_field_value=params[band_metadata]).update()
                else:
                    pass
                gxiba.GXIBA_CLOUD_STORAGE_INTERFACE.copy(bucket_source_path, bucket_save_path)
            elif name[-4:] in ['.TIF']:
                logger.debug(f'......Attempting to insert metadata from {image_metadata.platform}:{name}')
                platform_id = image_metadata.platform_id
                try:
                    params = landsat_parser.match(name).groupdict()
                except AttributeError:
                    continue
                if params is not None:
                    params.update({
                        'project_location_url': bucket_save_path,
                        'platform_id': platform_id,
                        'status': 'BandMetadataProcessed'})
                    for band_metadata in params:
                        if band_metadata != 'band' and band_metadata != platform_id:
                            logger.debug(
                                f'...Adding {band_metadata} from {platform_id}, band {params["band"]} to database.')
                            gxiba.BandMetadata(
                                platform_id=platform_id,
                                band=params['band'],
                                metadata_field_name=band_metadata,
                                metadata_field_value=params[band_metadata]).update()
                else:
                    pass
                gxiba.GXIBA_CLOUD_STORAGE_INTERFACE.copy(bucket_source_path, bucket_save_path)
            else:
                logger.debug('......Ignored for missing data naming convention filter.')
    except Exception:
        logger.exception(f'Something went wrong with {image_metadata}')


multithreading = True


def update_database_metadata():
    processed_image_counter = 0
    for location in gxiba.GXIBA_LOCATIONS:
        for key in location:
            logger.debug(key)
            if multithreading:
                with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
                    future_to_url = {
                        executor.submit(process_image_metadata, image_metadata): image_metadata for image_metadata in
                        get_image_metadata_from_big_query(
                            latitude=location[key]['latitude'],
                            longitude=location[key]['longitude'])}
                    for future in concurrent.futures.as_completed(future_to_url):
                        processed_image_counter += 1
                        logger.debug(f'Thread processing finished with status {future}.\n'
                                     f'{processed_image_counter} images currently processed.')
                    logger.debug('Finished creating metadata from Big Query.')
            else:
                for image_metadata in get_image_metadata_from_big_query(
                        latitude=location[key]['latitude'],
                        longitude=location[key]['longitude']):
                    process_image_metadata(image_metadata)
                    processed_image_counter += 1
                logger.debug('Finished creating metadata from Big Query.')
    return processed_image_counter


if __name__ == '__main__':
    logger.debug('Beginning processing.')
    start_time = perf_counter()
    count = update_database_metadata()
    finish_time = perf_counter()
    logger.debug(f'Processed {count} images in {finish_time - start_time}.')
