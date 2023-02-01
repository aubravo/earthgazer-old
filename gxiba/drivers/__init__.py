from abc import abstractmethod
from typing import Protocol


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
