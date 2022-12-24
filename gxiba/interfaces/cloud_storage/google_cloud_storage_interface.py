import io
import logging

from gxiba.storage import CloudStorageInterface
from google.cloud import storage
from google.oauth2 import service_account


class GoogleCloudStorageInterface(CloudStorageInterface):
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

    def upload(self, local_path, remote_path):
        # TODO Implement upload GCS Storage method!
        # labels: enhancement
        raise NotImplementedError


