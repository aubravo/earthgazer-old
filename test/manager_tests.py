import json
import os
from pathlib import Path
import shutil
import unittest


from gxiba import CloudStorageManager, LocalStorageManager, GoogleCloudStorageInterface


class StorageManagerTest(unittest.TestCase):
    def setUp(self):
        self.test_temp_path_string = "./tmp/"
        self.test_temp_path = Path(self.test_temp_path_string)
        self.test_temp_path.mkdir(parents=True, exist_ok=True)

    def test_local_manager(self):
        local_storage_manager = LocalStorageManager()
        self.assertIn('.gxiba', local_storage_manager.project_path)

    def test_cloud_storage_manager_filepath(self):
        local_storage_manager = LocalStorageManager()
        with open(local_storage_manager.project_path + 'keys.json') as keys:
            cloud_storage_keys = json.loads(keys.read())
        cloud_storage_manager = CloudStorageManager(GoogleCloudStorageInterface, cloud_storage_keys)
        cloud_storage_manager.download('gs://gxiba-storage/separate_bands.png', f'{self.test_temp_path_string}download_as_filepath.jpg')
        self.assertEqual(os.path.getsize(f'{self.test_temp_path_string}download_as_filepath.jpg'), os.path.getsize('../docs/images/separate_bands.png'))

    def test_cloud_storage_manager_iostream(self):
        local_storage_manager = LocalStorageManager()
        with open(local_storage_manager.project_path + 'keys.json') as keys:
            cloud_storage_keys = json.loads(keys.read())
        cloud_storage_manager = CloudStorageManager(GoogleCloudStorageInterface, cloud_storage_keys)
        with open(f'{self.test_temp_path_string}download_as_iostream.jpg', 'wb') as save_file:
            cloud_storage_manager.download('gs://gxiba-storage/Band_merge.png', save_file)
        self.assertEqual(os.path.getsize(f'{self.test_temp_path_string}download_as_iostream.jpg'), os.path.getsize('../docs/images/Band_merge.png'))

    def tearDown(self):
        shutil.rmtree(self.test_temp_path)

if __name__ == '__main__':
    unittest.main()
