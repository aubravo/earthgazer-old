from datetime import datetime
import logging
from typing import Iterable

import gxiba.data_sources.bigquery as gxiba_bigquery
import gxiba.data_objects.definitions as definitions
from gxiba import ImageMetadata

logger = logging.getLogger(__name__)


def create_gxiba_image_metadata_from_big_query(bigquery_interface: gxiba_bigquery.BigQueryInterface, engine,
                                               platform: definitions.SatelliteImagePlatform | str,
                                               latitude: float = None,
                                               longitude: float = None,
                                               from_date: datetime = None,
                                               to_date: datetime = None,
                                               order_asc: bool = True) -> Iterable[ImageMetadata]:

    if isinstance(platform, str):
        platform = definitions.SatelliteImagePlatform(platform)
    elif not isinstance(platform, definitions.SatelliteImagePlatform):
        raise NotImplementedError(f'Expected str or gxiba.SatelliteImagePlatform, got {type(platform)} instead.')
    query_constructor_buffer = "SELECT "
    query_constructor_buffer += ',\n'.join([f'{platform.database_mapping[member]} as {member}' for member in platform.database_mapping.keys()])
    query_constructor_buffer += f",\n\"{definitions.ImageProcessingStatus.BigQueryImport.name}\" as status\nFROM {platform.big_query_path}\n"
    queries=[]
    if latitude:
        queries.append(f"{platform.database_mapping['latitude_north']} >= {latitude} \nAND {platform.database_mapping['latitude_south']} <= {latitude}")
    if longitude:
        queries.append(f"{platform.database_mapping['longitude_east']} >= {longitude} \nAND {platform.database_mapping['longitude_west']} <= {longitude}")
    if from_date:
        queries.append([f"""sensing_time > '{from_date}'"""])
    if to_date:
        queries.append([f"""sensing_time < '{to_date}'"""])

    if queries:
        query_constructor_buffer += f"WHERE " + '\nAND '.join([query for query in queries])

    if order_asc:
        query_constructor_buffer += """\nORDER BY sensing_time ASC"""

    logger.debug(query_constructor_buffer)

    bigquery_results = bigquery_interface.query(query_constructor_buffer)
    total_rows = bigquery_results.result().total_rows
    for row in bigquery_results:
        yield ImageMetadata(*row), total_rows
