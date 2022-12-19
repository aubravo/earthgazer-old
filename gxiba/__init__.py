from gxiba.storage_manager import LocalStorageManager, CloudStorageManager
from gxiba.storage_manager.google_cloud_storage_interface import GoogleCloudStorageInterface
from gxiba.image_processor import ImageProcessor
from gxiba.database_manager import DataBaseManager
from gxiba.database_manager.sqllite_engine import SQLiteDataBaseEngine
from gxiba.database_manager.postgres_engine import PostgresDataBaseEngine
from gxiba.gxiba_dataclasses import GxibaImageMetadata
from gxiba.data_importer import BigQueryInterface

POPOCATEPETL_CRATER_LATITUDE = 19.023370
POPOCATEPETL_CRATER_LONGITUDE = -98.622864

SENTINEL_2_BIGQUERY_PATH = "bigquery-public-data.cloud_storage_geo_index.sentinel_2_index"

# For testing only imports
import json # NoQA


def test_get_image_metadata():
    local_storage_manager = LocalStorageManager()
    with open(f'{local_storage_manager.project_path}keys.json') as keys:
        google_keys = json.loads(keys.read())
    big_query_interface = BigQueryInterface(google_keys)
    query_text = f"""
        SELECT * FROM {SENTINEL_2_BIGQUERY_PATH} WHERE
        granule_id LIKE "L1C%" AND
        north_lat >= {POPOCATEPETL_CRATER_LATITUDE} AND
        south_lat <= {POPOCATEPETL_CRATER_LATITUDE} AND
        east_lon >= {POPOCATEPETL_CRATER_LONGITUDE} AND
        west_lon <= {POPOCATEPETL_CRATER_LONGITUDE} """
    print(query_text)
    db_manager = DataBaseManager(SQLiteDataBaseEngine, f'{local_storage_manager.project_path}test.db')
    response = big_query_interface.query(query_text)
    for row in response:
        image = GxibaImageMetadata(
            platform='SENTINEL_2',
            platform_id=row['granule_id'],
            sensing_time=row['sensing_time'].isoformat(),
            latitude_north=row['north_lat'],
            latitude_south=row['south_lat'],
            longitude_east=row['east_lon'],
            longitude_west=row['west_lon'],
            base_url=row['base_url'],
            status='GET-METADATA')
        image.push_to_database(db_manager)


if __name__ == "__main__":
    local_storage_manager = LocalStorageManager()
    with open(f'{local_storage_manager.project_path}keys.json') as keys:
        google_keys = json.loads(keys.read())
    db_manager = DataBaseManager(SQLiteDataBaseEngine, f'{local_storage_manager.project_path}test.db')
    test = GxibaImageMetadata.get_from_platform_id('L1C_T14QNG_A010076_20170527T171409', db_manager)
    print(test.platform)
