import logging
import os
import time

from earthgazer.config import Configuration
from earthgazer.local_environment import LOCAL_PROJECT_CONFIG_PATH

logging.info(f'Initializing environment setup.')
setup_start_time = time.time()

if os.path.exists(LOCAL_PROJECT_CONFIG_PATH):
    logging.info('Importing configuration from already existing project configuration file.')
    GXIBA_CONFIGURATION = Configuration.parse_file(LOCAL_PROJECT_CONFIG_PATH)
else:
    logging.info('No project configuration file found. Attempting to create one from defaults.')
    GXIBA_CONFIGURATION = Configuration()
    with open(LOCAL_PROJECT_CONFIG_PATH, 'w+') as config_file:
        config_file.write(GXIBA_CONFIGURATION.json())
    logging.info('Project configuration file created succesfully.')

setup_end_time = time.time()
logging.info(f'Environment setup completed in {setup_end_time - setup_start_time}.')

del setup_start_time, setup_end_time
