import logging

import fsspec

from earthgazer.settings import EarthGazerSettings
from earthgazer.utils import Singleton


class FileSystems(metaclass=Singleton):
    def __init__(self):
        for file_system_name, file_system_settings in EarthGazerSettings().file_manager.items():  # type: ignore
            try:
                setattr(self, file_system_name, fsspec.filesystem(**file_system_settings.dict()))
            except Exception as e:
                logging.error(f"Failed to initialize {file_system_name} with settings {file_system_settings.dict()}")
                raise e
        logging.info(f"Initialized {len(self.__dict__)} file systems:")
        for x in self.__dict__:
            logging.info(f"\t{x} as type {self.__dict__[x].protocol}.")

    def get_by_name(self, file_system_name):
        return getattr(self, file_system_name)
