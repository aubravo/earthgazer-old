from abc import abstractmethod
from typing import Callable, Protocol


class CloudStorageInterface:
    def __init__(self, driver: Callable, credentials: dict = None):
        if credentials is None:
            credentials = {}
        self._cloud_storage_interface = driver(credentials)

    @property
    def interface(self):
        return self._cloud_storage_interface

    def download(self, remote_path, local_path):
        self._cloud_storage_interface.download(remote_path, local_path)

    def upload(self, local_path, remote_path):
        self._cloud_storage_interface.upload(local_path, remote_path)

    def copy(self, source_path, destination_path):
        self._cloud_storage_interface.copy(source_path, destination_path)

    def list(self, remote_path):
        yield from self._cloud_storage_interface.list(remote_path)


class AbstractCloudStorageDriver(Protocol):
    """Cloud Storage Interface.

    Template class for Cloud Storage Interfaces. See `gxiba.interfaces` for implementations."""

    def __init__(self, credentials):
        self.client_ = self.client_start(credentials)

    @property
    def client(self):
        return self.client_

    @abstractmethod
    def client_start(self, credentials: dict) -> object:
        """In order for the Storage Manager to work properly, it requires this method to execute all the initialization
        logic which will be executed upon instance creation unless the `__init__` method is overriden.

        If a client object is required, it needs to be returned by this method to be accessible under the only-read
        `interface` property."""
        ...

    @abstractmethod
    def copy(self, source_path, destination_path):
        ...

    @abstractmethod
    def download(self, remote_path, local_path):
        ...

    @abstractmethod
    def list(self, remote_path):
        ...

    @abstractmethod
    def upload(self, local_path, remote_path):
        ...
