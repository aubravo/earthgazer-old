import logging
from dataclasses import dataclass, field, asdict
from datetime import datetime

from sqlalchemy import Column, Text, Numeric, DateTime, asc, desc, Integer

from gxiba.environment import MAPPER_REGISTRY, GXIBA_DATABASE_ENGINE, GXIBA_DATABASE_SESSION, GXIBA_DATABASE_SCHEMA

logger = logging.getLogger(__name__)

logger.debug('Starting database objects creation')


class GxibaDataBaseObject:

    _in_database: bool
    create_timestamp: datetime
    last_update_timestamp: datetime

    def update(self):
        if not self._in_database:
            self.create_timestamp = datetime.now()
            self.last_update_timestamp = datetime.now()
            GXIBA_DATABASE_SESSION.add(self)
            GXIBA_DATABASE_SESSION.commit()
            self._in_database = True
        else:
            self.last_update_timestamp = datetime.now()
            GXIBA_DATABASE_SESSION.commit()

    def drop(self):
        GXIBA_DATABASE_SESSION.delete(self)

    @property
    def as_dict(self) -> dict:
        return asdict(self)


logger.debug('...Passing BandMetadata object to MAPPER_REGISTRY')


@MAPPER_REGISTRY.mapped
@dataclass
class BandMetadata(GxibaDataBaseObject):
    __tablename__ = "band_metadata"
    if 'sqlite' not in GXIBA_DATABASE_ENGINE.name.lower():
        __table_args__ = {"schema": GXIBA_DATABASE_SCHEMA}
    __sa_dataclass_metadata_key__ = "sa"

    platform_id: str = field(metadata={"sa": Column(Text, primary_key=True)})
    band: int = field(metadata={"sa": Column(Integer, primary_key=True)})
    metadata_field_name: str = field(metadata={"sa": Column(Text, primary_key=True)})
    metadata_field_value: str = field(metadata={"sa": Column(Text)})
    metadata_field_type: str = field(default='', metadata={"sa": Column(Text)})
    status: str = field(default='', metadata={"sa": Column(Text)})
    create_timestamp: datetime = field(default_factory=datetime.now, metadata={"sa": Column(DateTime)})
    last_update_timestamp: datetime = field(default_factory=datetime.now, metadata={"sa": Column(DateTime)})
    _in_database: bool = False

    def __post_init__(self):
        self._in_database = False


logger.debug('...Passing ImageMetadata object to MAPPER_REGISTRY')


@ MAPPER_REGISTRY.mapped
@ dataclass
class ImageMetadata(GxibaDataBaseObject):
    __tablename__ = "image_metadata"
    if 'sqlite' not in GXIBA_DATABASE_ENGINE.name.lower():
        __table_args__ = {"schema": GXIBA_DATABASE_SCHEMA}
    __sa_dataclass_metadata_key__ = "sa"

    platform_id: str = field(metadata={"sa": Column(Text, primary_key=True)})
    platform: str = field(metadata={"sa": Column(Text)})
    sensing_time: datetime = field(metadata={"sa": Column(DateTime)})
    latitude_north: float = field(metadata={"sa": Column(Numeric)})
    latitude_south: float = field(metadata={"sa": Column(Numeric)})
    longitude_west: float = field(metadata={"sa": Column(Numeric)})
    longitude_east: float = field(metadata={"sa": Column(Numeric)})
    base_url: str = field(metadata={"sa": Column(Text)})
    status: str = field(metadata={"sa": Column(Text)})
    usage: str = field(default='', metadata={"sa": Column(Text)})
    create_timestamp: datetime = field(default_factory=datetime.now, metadata={"sa": Column(DateTime)})
    last_update_timestamp: datetime = field(default_factory=datetime.now, metadata={"sa": Column(DateTime)})
    _in_database: bool = False

    def __post_init__(self):
        self._in_database = False


logger.debug('...Attempting to create all objects associated with MAPPER_REGISTRY')
MAPPER_REGISTRY.metadata.create_all(bind=GXIBA_DATABASE_ENGINE, checkfirst=True)


# =====================================================
# ================Interaction Methods==================
# =====================================================

def database_query(database_object, query_filters=None, order_by_parameter=None, order='asc'):
    if query_filters is None:
        query_filters = []
    query = GXIBA_DATABASE_SESSION.query(database_object)
    for query_filter in query_filters:
        query = query.filter(query_filter)
    if order_by_parameter:
        if order.lower() == 'asc':
            query = query.order_by(asc(order_by_parameter))
        elif order.lower() == 'desc':
            query = query.order_by(desc(order_by_parameter))
        else:
            raise NotImplementedError
    for result in query:
        result._in_database = True
        yield result
