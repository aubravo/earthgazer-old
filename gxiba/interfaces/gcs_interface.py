import io
import logging
import re
from collections.abc import Generator

from google.cloud import storage
from google.cloud.storage import Bucket, Blob
from google.oauth2 import service_account

from gxiba.storage import CloudStorageInterface


def get_bucket_name(path):
    regex_bucket_path_finder = '^gs://(.*?)/(.*)$'
    re_match = re.match(regex_bucket_path_finder, path)
    return re_match[1]


def get_blob_name(path):
    regex_bucket_path_finder = '^gs://(.*?)/(.*)$'
    re_match = re.match(regex_bucket_path_finder, path)
    return re_match[2]


class GoogleCloudStorageInterface(CloudStorageInterface):

    def __init__(self, credentials):
        self._source_bucket = None
        self._destination_bucket = None
        super().__init__(credentials)

    def new_client(self, credentials: dict) -> storage.client.Client:
        service_account_credentials = service_account.Credentials.from_service_account_info(
            credentials,
            scopes=["https://www.googleapis.com/auth/cloud-platform"]
        )

        logging.debug('Credentials ready.')
        storage_client = storage.client.Client(
            credentials=service_account_credentials,
            project=service_account_credentials.project_id
        )
        logging.debug('Google Storage Client successfully created')
        return storage_client

    def download(self, remote_path, local_file: io.FileIO | str) -> None:
        if type(local_file) == io.BufferedWriter:
            logging.debug('Downloading file into FileIO.')
            self.client.download_blob_to_file(remote_path, local_file)
        elif type(local_file) == str:
            with open(local_file, 'wb') as save_file:
                logging.debug('Downloading file to provided path.')
                self.client.download_blob_to_file(remote_path, save_file)
        else:
            raise NotImplementedError(f'{type(local_file)} not supported.')

    def get_source_bucket(self, bucket_name):
        self._source_bucket = Bucket(self.client, name=bucket_name)
        return self._source_bucket

    def get_destination_bucket(self, bucket_name):
        self._destination_bucket = Bucket(self.client, name=bucket_name)
        return self._destination_bucket

    @property
    def source_bucket(self):
        return self._source_bucket

    @property
    def destination_bucket(self):
        return self._destination_bucket

    def list(self, remote_path) -> Generator[str]:
        self.get_source_bucket(f'{get_bucket_name(remote_path)}')
        for blob in self.client.list_blobs(self.source_bucket,
                                        prefix=remote_path[len(f'gs://{self.source_bucket.name}/'):],
                                        fields='items/name'):
            yield blob.name

    def copy(self, source_path, destination_path):
        self.get_destination_bucket(f'{get_bucket_name(destination_path)}')
        destination_blob = Blob(f'{get_blob_name(destination_path)}', self.destination_bucket)
        if not destination_blob.exists():
            print(f'rewriting {destination_blob}')
            self.get_source_bucket(f'{get_bucket_name(source_path)}')
            destination_blob.rewrite(self.source_bucket.blob(f'{get_blob_name(source_path)}'))
        else:
            print('Blob already exists.')

    def upload(self, local_path, remote_path):
        ...
