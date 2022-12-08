import logging
import json
import unittest

from gxiba import CloudStorageManager, LocalStorageManager, GoogleCloudStorageInterface


class StorageManagerTest(unittest.TestCase):
    def local_manager_test(self):
        x = LocalStorageManager()
        self.assertIn('.gxiba', x.project_path)

    def cloud_storage_manager(self):
        with open(x.project_path + 'keys.json') as keys:
            cloud_storage_keys = json.loads(keys.read())
        y = CloudStorageManager(GoogleCloudStorageInterface, cloud_storage_keys)
        logging.debug('Trying to download test file')

        y.download('gs://gxiba-storage/test.jpg', './test1.jpg')

        with open('./test2.jpg', 'wb') as save_file:
            print(type(save_file))
            logging.debug('Test file open')
            y.download('gs://gxiba-storage/test.jpg', save_file)
            logging.debug('Download with no errors')
