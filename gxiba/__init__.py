from gxiba.bigquery import BigQueryInterface
from gxiba.data_objects import GxibaImageMetadata, SatelliteImagePlatform, ImageProcessingStatus, BigQueryPath, \
    database_get_from_platform_id, database_get_from_point, big_query_get_by_point
from gxiba.database import DataBaseInterface
from gxiba.image_processor import ImageProcessor
from gxiba.interfaces.gcs_interface import GoogleCloudStorageInterface
from gxiba.local_storage import LocalStorageManager
from gxiba.cloud_storage import CloudStorageManager

POPOCATEPETL_CRATER_LATITUDE = 19.023370
POPOCATEPETL_CRATER_LONGITUDE = -98.622864

# For testing only imports
import json  # NoQA

if __name__ == "__main__":
    local_storage = LocalStorageManager()
    db_interface = DataBaseInterface()
    with open(f'{local_storage.project_path}keys.json') as keys:
        google_keys = json.loads(keys.read())
    gcs_client = CloudStorageManager(GoogleCloudStorageInterface, google_keys)
    gxiba_images = database_get_from_point(db_interface, POPOCATEPETL_CRATER_LATITUDE, POPOCATEPETL_CRATER_LONGITUDE,
                                           status=ImageProcessingStatus.BigQueryImport.name)
    for x in gxiba_images:
        print(f'STARTING download of {x.platform_id} images.')
        y = gcs_client.list(x.base_url)
        for name in y:
            try:
                if name[-4:] in ['.jp2'] and any(folder in name for folder in ['IMG_DATA']):
                    gcs_client.copy(f'gs://{gcs_client.interface.source_bucket.name}/{name}',
                                    f'gs://gxiba-storage/{x.platform_id}/{name.split("/")[-1]}')
                    # gcs_client.download(f'gs://{gcs_client.interface.source_bucket.name}/{name}', f'C:/Users/alvaro.bravo/.gxiba/{x.platform_id}/{name.split("/")[-1]}')
            except Exception as e:
                raise Exception(e)
        x.status = ImageProcessingStatus.ProjectStorage.name
        x.update(db_interface)
