import logging
import os
import pathlib
import time
from os.path import isdir

logger = logging.getLogger(__name__)


def execute_setup():
    logger.info(f'Initializing environment setup.')
    setup_start_time = time.time()

    setup_end_time = time.time()
    logger.info(f'Environment setup completed in {setup_end_time - setup_start_time}.')

    del setup_start_time, setup_end_time


if __name__ == '__main__':
    execute_setup()
