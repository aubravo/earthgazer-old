# Data Handling
from gxiba.database import DataBaseInterface
from gxiba.data_objects import GxibaImageMetadata, SatelliteImagePlatform, ImageProcessingStatus

# Data import
from gxiba.data_importer import BigQueryInterface, BIGQUERY_PATH_SENTINEL_2, BIGQUERY_PATH_LANDSAT_8

# Storage
from gxiba.storage import LocalStorageManager, CloudStorageManager
from gxiba.interfaces.cloud_storage.google_cloud_storage_interface import GoogleCloudStorageInterface

from gxiba.image_processor import ImageProcessor

POPOCATEPETL_CRATER_LATITUDE = 19.023370
POPOCATEPETL_CRATER_LONGITUDE = -98.622864

# For testing only imports
import json  # NoQA


def test_1():
    local_storage_manager = LocalStorageManager()
    with open(f'{local_storage_manager.project_path}keys.json') as keys:
        google_keys = json.loads(keys.read())
    big_query_interface = BigQueryInterface(google_keys)
    # test = DataBaseManager('postgresql', username='postgres', password='8p7mQG3Am4e?bLgf', host='34.170.25.88',
    #                       port='5432', database='postgres')
    query_text = f"""
                SELECT * FROM {BIGQUERY_PATH_SENTINEL_2} WHERE
                granule_id LIKE "L1C%" AND
                north_lat >= {POPOCATEPETL_CRATER_LATITUDE} AND
                south_lat <= {POPOCATEPETL_CRATER_LATITUDE} AND
                east_lon >= {POPOCATEPETL_CRATER_LONGITUDE} AND
                west_lon <= {POPOCATEPETL_CRATER_LONGITUDE} """
    response = big_query_interface.query(query_text)
    gxiba_images_list = []
    for row in response:
        gxiba_images_list.append(GxibaImageMetadata(
            platform_id=row['granule_id'], platform=SatelliteImagePlatform.SENTINEL2.value,
            sensing_time=row['sensing_time'],
            latitude_north=row['north_lat'], latitude_south=row['south_lat'],
            longitude_east=row['east_lon'], longitude_west=row['west_lon'],
            base_url=row['base_url'],
            usage='', status=ImageProcessingStatus.BigQueryImport.name))
    test.add(gxiba_images_list)


if __name__ == "__main__":
    test = DataBaseInterface()
    x = GxibaImageMetadata.get_from_platform_id('L1C_T14QNG_A009504_20170417T171425', test)
    print(x)
