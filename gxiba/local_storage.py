import logging
import os
from pathlib import Path


class LocalStorageManager:
    def __init__(self):
        self.user_home_path_ = os.path.expanduser("~")
        self.project_home_path_ = f'{os.path.expanduser("~")}/.gxiba/'
        logging.debug(f'Attempting to create project path in {self.project_path}')
        project_path = Path(self.project_path)
        project_path.mkdir(parents=True, exist_ok=True)
        logging.debug(f'Project path was created successfully or already exists.')

    @property
    def user_home_path(self) -> str:
        return self.user_home_path_

    @property
    def project_path(self) -> str:
        return self.project_home_path_
