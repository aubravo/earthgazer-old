import concurrent.futures
import logging
import re
from datetime import datetime
from typing import Iterable

try:
    import gxiba
except ModuleNotFoundError:
    from pathlib import Path
    import sys

    root_path = Path(__file__).parents[1]
    sys.path.append(str(root_path))
    import gxiba

logger = logging.getLogger(__name__)


def update_database_metadata():
    landsat_parser = re.compile(r'L(?P<sensor>[a-zA-Z])'
                                r'(?P<satellite>\d{2})_'
                                r'(?P<level>\w{4})_'
                                r'(?P<wrs_path>\d{3})'
                                r'(?P<wrs_row>\d{3})_'
                                r'(?P<acquisition_year>\d{4})'
                                r'(?P<acquisition_month>\d{2})'
                                r'(?P<acquisition_day>\d{2})_'
                                r'(?P<processing_year>\d{4})'
                                r'(?P<processing_month>\d{2})'
                                r'(?P<processing_day>\d{2})_'
                                r'(?P<collection_number>\d{2})_'
                                r'(?P<collection_category>[A-Z]\w)_B'
                                r'(?P<band>\d{1,2}).TIF')

    def get_image_metadata_from_big_query(platform: gxiba.SatelliteImagePlatform | str,
                                          latitude: float = None,
                                          longitude: float = None,
                                          from_date: datetime = None,
                                          to_date: datetime = None,
                                          order_asc: bool = True) -> Iterable[gxiba.ImageMetadata]:
        logger.debug('Starting create gxiba image metadata from big query process.')
        logger.debug(f'...Platform: {platform}')
        logger.debug(f'...Latitude: {latitude if latitude else "Not defined"}')
        logger.debug(f'...Longitude: {longitude if longitude else "Not defined"}')
        logger.debug(f'...From date: {from_date if from_date else "Not defined"}')
        logger.debug(f'...To date: {to_date if to_date else "Not defined"}')

        query_constructor_buffer = "SELECT "
        query_constructor_buffer += ',\n'.join(
            [f'{platform.database_mapping[member]} as {member}' for member in platform.database_mapping.keys()])
        query_constructor_buffer += f",\n\"{gxiba.ImageProcessingStatus.BigQueryImport.name}\" as status\nFROM {platform.big_query_path}\n"
        queries = []
        if latitude:
            queries.append(
                f"{platform.database_mapping['latitude_north']} >= {latitude} \nAND {platform.database_mapping['latitude_south']} <= {latitude}")
        if longitude:
            queries.append(
                f"{platform.database_mapping['longitude_east']} >= {longitude} \nAND {platform.database_mapping['longitude_west']} <= {longitude}")
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

    def process_image_metadata(image_metadata):
        logger.debug(f'...Adding: {image_metadata.platform_id} to Image Metadata table.')
        image_metadata.update()
        logger.info(f'...Beginning download of {image_metadata.platform_id} images.')
        blobs = gxiba.GXIBA_CLOUD_STORAGE_INTERFACE.list(image_metadata.base_url)
        for name in blobs:
            # TODO: Fix hardcoded gs bucket path.
            bucket_source_path = f'gs://{gxiba.GXIBA_CLOUD_STORAGE_INTERFACE.interface.source_bucket.name}/{name}'
            bucket_save_path = f'gs://{gxiba.GXIBA_CLOUD_STORAGE_BUCKET}/{image_metadata.platform_id}/{name.split("/")[-1]}'
            logger.debug(f'......Attempting to copy file "{name}" to own bucket.')
            if name[-4:] in ['.jp2'] and any(folder in name for folder in ['IMG_DATA']):
                # TODO: Implement sentinel nameparser
                # labels: enhancement
                raise NotImplementedError
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
                        'status': 'testing'})
                    for band_metadata in params:
                        if band_metadata != 'band':
                            logger.debug(
                                f'...Adding {band_metadata} from {platform_id}, band {params["band"]} to database.')
                            BandMetadata(
                                platform_id=platform_id,
                                band=params['band'],
                                metadata_field_name=band_metadata,
                                metadata_field_value=params[band_metadata]).update()
                else:
                    pass
                gxiba.GXIBA_CLOUD_STORAGE_INTERFACE.copy(bucket_source_path, bucket_save_path)
            else:
                logger.debug('......Ignored for missing data naming convention.')
        image_metadata.status = gxiba.ImageProcessingStatus.ProjectStorage.name
        logger.info(f'{image_metadata.platform_id} status changed to {image_metadata.status}')
        image_metadata.update()

    for location in gxiba.GXIBA_LOCATIONS:
        for key in location:
            logger.debug(key)
            with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
                future_to_url = {
                    executor.submit(process_image_metadata, image_metadata): image_metadata for image_metadata in
                    get_image_metadata_from_big_query(
                        platform=gxiba.SatelliteImagePlatform.LANDSAT_8,
                        latitude=location[key]['latitude'],
                        longitude=location[key]['longitude'])}
                for future in concurrent.futures.as_completed(future_to_url):
                    logger.debug(f'Thread processing finished with status {future}')
                logger.debug('Finished creating metadata from Big Query.')


if __name__ == '__main__':
    logger.debug('Beginning processing.')
    update_database_metadata()
