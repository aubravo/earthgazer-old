"""Storage manager.

This module provides interfaces to create and manage local storage, download and upload files to cloud storage.
"""

from abc import abstractmethod
from collections.abc import Callable
import logging
import os
from pathlib import Path
from typing import Protocol, Any


class CloudStorageInterface(Protocol):
    """Cloud Storage Manager.

    This protocol class acts as a template for creating Cloud Storage Interfaces with different providers.
    """

    client_: Any

    def __init__(self, credentials):
        self.client_ = self.new_client(credentials)

    @property
    def client(self):
        return self.client_

    @abstractmethod
    def new_client(self, credentials: dict) -> object:
        """In order for the Storage Manager to work properly, it requires this method to execute all the initialization
        logic which will be executed upon instance creation unless the __init__ method is overriden.

        If a client object is required, it needs to be returned by this method to be accessible under the only-read
        client property.
        """
        ...

    @abstractmethod
    def download(self, remote_path, local_file):
        ...

    @abstractmethod
    def upload(self, local_file, remote_path):
        ...

    @abstractmethod
    def list(self, remote_path):
        ...

    @abstractmethod
    def copy(self, source_path, destination_path):
        ...


class LocalStorageManager:
    def __init__(self):
        self.user_home_path_ = os.path.expanduser("~")
        self.project_home_path_ = f'{os.path.expanduser("~")}/.gxiba/'
        self._create_project_path()

    @property
    def user_home_path(self) -> str:
        return self.user_home_path_

    @property
    def project_path(self) -> str:
        return self.project_home_path_

    def _create_project_path(self) -> None:
        logging.debug(f'Attempting to create project path in {self.project_path}')
        project_path = Path(self.project_path)
        project_path.mkdir(parents=True, exist_ok=True)
        logging.debug(f'Project path already exists or was created successfully.')


class CloudStorageManager:
    def __init__(self, cloud_storage_interface: Callable, credentials: dict = None):
        if credentials is None:
            credentials = {}
        self._cloud_storage_interface = cloud_storage_interface(credentials)

    @property
    def client(self):
        return self._cloud_storage_interface.client

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

