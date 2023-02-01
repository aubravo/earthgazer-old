import logging
import datetime

import gxiba.environment


logger = logging.getLogger(__name__)
logger.info('Gxiba environment started correctly. Now you can start doing things.')

exit(0)

# TODO: Prepare for unittest

import random
import string

from_date = datetime.datetime.fromisoformat('2021-12-31')
to_date = datetime.datetime.fromisoformat('2023-12-31')

filters = [gxiba.environment.BandMetadata.create_timestamp >= from_date,
           gxiba.environment.BandMetadata.create_timestamp <= to_date]

letters = string.ascii_letters + string.digits


def random_word(length: int) -> str:
    return ''.join(random.choice(letters) for i in range(length))


def random_band_metadata():
    return gxiba.environment.BandMetadata(
        platform_id=random_word(10),
        band=random.randint(0, 15),
        metadata_field_name=random_word(10),
        metadata_field_value=random_word(10),
        metadata_field_type=random_word(10),
        status='PROCESSING')


def test_database_insertion_and_update():
    logger.debug('Beginning database methods testing.')

    for _ in range(0, 10):
        data_obj = random_band_metadata()
        data_obj.update()
        logger.debug(f'...Testing new registry saving in BandMetadata {_ + 1}/10')
        if random.choice([True, False]):
            data_obj.status = 'TESTING'
            data_obj.update()
        logger.debug(f'...Testing field updates in BandMetadata {_ + 1}/10')

    for data_obj in gxiba.environment.database_query(gxiba.environment.BandMetadata, query_filters=filters, order_by_parameter=gxiba.environment.BandMetadata.band, order='desc'):
        data_obj.status = 'CHANGE TEST'
        data_obj.update()
        logger.debug(data_obj)
        logger.debug(f'...Testing field updates in BandMetadata objects retrieved from query-'
                     f'create timestamp: {data_obj.create_timestamp}, last update timestamp: {data_obj.last_update_timestamp}')
        data_obj.drop()

    logger.debug(f'...Drop test:')
    for data_obj in gxiba.environment.database_query(gxiba.environment.BandMetadata):
        logger.warning(f'{data_obj} still found in BandMetadata table.')
        raise AssertionError
    logger.debug(f'...No records found. BandMetadata table contents dropped successfully.')
    logger.info(f'Tests completed successfully!')


test_database_insertion_and_update()
