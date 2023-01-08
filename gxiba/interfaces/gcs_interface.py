import io
import logging
import re
from collections.abc import Generator

from google.cloud import storage
from google.cloud.storage import Bucket, Blob
from google.oauth2 import service_account

import gxiba.cloud_storage as gxiba_cloud_storage

regex_bucket_path_finder = '^gs://(.*?)/(.*)$'
logger = logging.getLogger(__name__)


def get_bucket_name(path):
    re_match = re.match(regex_bucket_path_finder, path)
    return re_match[1]


def get_blob_name(path):
    re_match = re.match(regex_bucket_path_finder, path)
    return re_match[2]


class GoogleCloudStorageInterface(gxiba_cloud_storage.CloudStorageInterface):

    def __init__(self, credentials):
        self._source_bucket = None
        self._destination_bucket = None
        super().__init__(credentials)

    def client_start(self, credentials: dict) -> storage.client.Client:
        service_account_credentials = service_account.Credentials.from_service_account_info(
            credentials,
            scopes=["https://www.googleapis.com/auth/cloud-platform"]
        )

        logger.debug('Credentials ready.')
        storage_client = storage.client.Client(credentials=service_account_credentials,
                                               project=service_account_credentials.project_id)
        logger.debug('Google Storage Client successfully created')
        return storage_client

    def download(self, remote_path, local_path: io.FileIO | str) -> None:
        if isinstance(local_path, io.FileIO):
            logger.debug('Downloading file into FileIO.')
            self.client.download_blob_to_file(remote_path, local_path)
        elif isinstance(local_path, str):
            with open(local_path, 'w+b') as save_file:
                logger.debug('Downloading file to provided path.')
                self.client.download_blob_to_file(remote_path, save_file)
        else:
            raise NotImplementedError(f'{type(local_path)} not supported.')

    def set_source_bucket(self, bucket_name):
        self._source_bucket = Bucket(self.client, name=bucket_name)
        return self._source_bucket

    def set_destination_bucket(self, bucket_name):
        self._destination_bucket = Bucket(self.client, name=bucket_name)
        return self._destination_bucket

    @property
    def source_bucket(self):
        return self._source_bucket

    @property
    def destination_bucket(self):
        return self._destination_bucket

    def list(self, remote_path) -> Generator[str]:
        self.set_source_bucket(f'{get_bucket_name(remote_path)}')
        for blob in self.client.list_blobs(self.source_bucket,
                                           prefix=remote_path[len(f'gs://{self.source_bucket.name}/'):],
                                           fields='items/name'):
            yield blob.name

    def copy(self, source_path, destination_path):
        self.set_destination_bucket(f'{get_bucket_name(destination_path)}')
        destination_blob = Blob(f'{get_blob_name(destination_path)}', self.destination_bucket)
        if not destination_blob.exists():
            logger.debug(f'Copying {destination_blob.name}')
            self.set_source_bucket(f'{get_bucket_name(source_path)}')
            destination_blob.rewrite(self.source_bucket.blobs(f'{get_blob_name(source_path)}'))
        else:
            self.set_source_bucket(f'{get_bucket_name(source_path)}')
            source_blob = self.source_bucket.blobs(f'{get_blob_name(source_path)}')
            destination_blob.reload()
            source_blob.reload()
            if destination_blob.crc32c == source_blob.crc32c:
                logger.info(f'Blob {destination_blob.name} already exists.')
            else:
                destination_blob.rewrite(self.source_bucket.blobs(f'{get_blob_name(source_path)}'))

    def upload(self, local_path, remote_path):
        destination_blob = Blob.from_string(remote_path, client=self.client)
        logger.debug(f'attempting to upload {local_path} to {remote_path}')
        with open(local_path, 'rb') as local_file:
            destination_blob.upload_from_file(local_file)
        logger.debug(f'{local_path} uploaded to {remote_path}')