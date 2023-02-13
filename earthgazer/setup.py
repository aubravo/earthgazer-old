import logging
import time

from earthgazer.config import Configuration

logger = logging.getLogger(__name__)


logger.info(f'Initializing environment setup.')
setup_start_time = time.time()

GXIBA_CONFIGURATION = Configuration.parse_file('configs_test.json')
print(dict(GXIBA_CONFIGURATION))

setup_end_time = time.time()
logger.info(f'Environment setup completed in {setup_end_time - setup_start_time}.')

del setup_start_time, setup_end_time
