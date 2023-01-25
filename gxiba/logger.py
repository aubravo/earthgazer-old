import logging
import logging.config
from pathlib import Path
import datetime


def setup_logger(log_path: str = None):

    if not log_path:
        log_path = Path(__file__).parents[1] / 'logs'
    else:
        log_path = Path(log_path)

    log_path.mkdir(parents=True, exist_ok=True)
    log_file_name = datetime.datetime.now().strftime('%Y%m%d')
    logging.config.fileConfig(f'{Path(__file__).parents[1]}/logging.dev.ini', disable_existing_loggers=False,
                              defaults={"logfilename": f'{log_path}/{log_file_name}.log'.replace('\\', '/')})