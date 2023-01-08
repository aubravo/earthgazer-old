import logging
import logging.config
from pathlib import Path
import datetime


def setup_logger():
    gxiba_main_path = Path(__file__).parents[1]
    gxiba_log_path = gxiba_main_path / 'logs'
    gxiba_log_path.mkdir(parents=True, exist_ok=True)
    log_file_name = datetime.datetime.now().strftime('%Y%m%d')
    logging.config.fileConfig(f'{gxiba_main_path}/logging.dev.ini', disable_existing_loggers=False,
                              defaults={"logfilename": f'{gxiba_log_path}/{log_file_name}.log'.replace('\\', '/')})
