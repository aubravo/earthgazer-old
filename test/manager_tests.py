import json
import os
import time
from pathlib import Path
import pandas
import shutil
import unittest

from gxiba import CloudStorageManager, LocalStorageManager, GoogleCloudStorageInterface
from gxiba import DataBaseManager, SQLiteDataBaseEngine


class StorageManagerTest(unittest.TestCase):
    def setUp(self):
        self.test_temp_path_string = "./tmp/"
        self.test_temp_path = Path(self.test_temp_path_string)
        self.test_temp_path.mkdir(parents=True, exist_ok=True)
        self.local_storage_manager = LocalStorageManager()

    def test_local_manager(self):
        self.assertIn('.gxiba', self.local_storage_manager.project_path)

    def test_cloud_storage_manager_filepath(self):
        with open(self.local_storage_manager.project_path + 'keys.json') as keys:
            cloud_storage_keys = json.loads(keys.read())
        cloud_storage_manager = CloudStorageManager(GoogleCloudStorageInterface, cloud_storage_keys)
        cloud_storage_manager.download('gs://gxiba-storage/test/separate_bands.png',
                                       f'{self.test_temp_path_string}download_as_filepath.jpg')
        self.assertEqual(os.path.getsize(f'{self.test_temp_path_string}download_as_filepath.jpg'),
                         os.path.getsize('../docs/images/separate_bands.png'))

    def test_cloud_storage_manager_iostream(self):
        with open(self.local_storage_manager.project_path + 'keys.json') as keys:
            cloud_storage_keys = json.loads(keys.read())
        cloud_storage_manager = CloudStorageManager(GoogleCloudStorageInterface, cloud_storage_keys)
        with open(f'{self.test_temp_path_string}download_as_iostream.jpg', 'wb') as save_file:
            cloud_storage_manager.download('gs://gxiba-storage/test/Band_merge.png', save_file)
        self.assertEqual(os.path.getsize(f'{self.test_temp_path_string}download_as_iostream.jpg'),
                         os.path.getsize('../docs/images/Band_merge.png'))

    def tearDown(self):
        shutil.rmtree(self.test_temp_path)


class DatabaseManagerTest(unittest.TestCase):
    def setUp(self) -> None:
        self.test_temp_path_string = "./tmp/"
        self.test_temp_path = Path(self.test_temp_path_string)
        self.test_temp_path.mkdir(parents=True, exist_ok=True)
        self.local_storage_manager = LocalStorageManager()

    def test_database_manager_sqlite(self):
        gxiba_database_manager = DataBaseManager(SQLiteDataBaseEngine,
                                                 f'{self.test_temp_path_string}test.db')
        gxiba_database_manager.execute("""  INSERT INTO gxiba_images
                                                (platform, platform_id, sensing_time,
                                                latitude_north, latitude_south, longitude_west, longitude_east,
                                                base_url, status)
                                                VALUES
                                                ('SENTINEL', 'nn2njio52ui3', '2022-11-30 23:45:00',
                                                19.9993, 19.99393992, 89.9299292, 98.929299292,
                                                'gs://test-path/something/something', 'TEST')""")

        database_response = gxiba_database_manager.query("""SELECT * FROM gxiba_images""")

        test_df = pandas.DataFrame({'id': [1],
                                    'platform': ['SENTINEL'],
                                    'platform_id': ['nn2njio52ui3'],
                                    'sensing_time': ['2022-11-30 23:45:00'],
                                    'latitude_north' :[19.9993],
                                    'latitude_south': [19.99393992],
                                    'longitude_west': [89.9299292],
                                    'longitude_east': [98.929299292],
                                    'base_url': ['gs://test-path/something/something'],
                                    'status': ['TEST']
                                    })

        gxiba_database_manager.close()
        self.assertTrue(database_response.equals(test_df))

    def tearDown(self):
        shutil.rmtree(self.test_temp_path)


if __name__ == '__main__':
    unittest.main()
