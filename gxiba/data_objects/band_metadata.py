import re
from dataclasses import dataclass, field, asdict
from datetime import datetime
import logging

from sqlalchemy import Column, Text, DateTime, Numeric, update, Integer

from gxiba.data_objects import mapper_registry


logger = logging.getLogger(__name__)

landsat_name_structure_parser = r'L(?P<sensor>[a-zA-Z])' \
                                r'(?P<satellite>\d{2})_' \
                                r'(?P<level>\w{4})_' \
                                r'(?P<wrs_path>\d{3})' \
                                r'(?P<wrs_row>\d{3})_' \
                                r'(?P<acquisition_year>\d{4})' \
                                r'(?P<acquisition_month>\d{2})' \
                                r'(?P<acquisition_day>\d{2})_' \
                                r'(?P<processing_year>\d{4})' \
                                r'(?P<processing_month>\d{2})' \
                                r'(?P<processing_day>\d{2})_' \
                                r'(?P<collection_number>\d{2})_' \
                                r'(?P<collection_category>[A-Z]\w)_B' \
                                r'(?P<band>\d{1,2}).TIF'

re_parser = name_parser = re.compile(landsat_name_structure_parser)


def __name_parser(file_name) -> dict | None:
    try:
        return re_parser.match(file_name).groupdict()
    except NotImplementedError:
        return None


@mapper_registry.mapped
@dataclass
class LandsatBandMetadata:
    __tablename__ = "landsat_band_metadata"
    __table_args__ = {"schema": "gxiba"}
    __sa_dataclass_metadata_key__ = "sa"

    sensor: str = field(metadata={"sa": Column(Text)})
    satellite: int = field(metadata={"sa": Column(Numeric)})
    level: str = field(metadata={"sa": Column(Text)})
    wrs_path: int = field(metadata={"sa": Column(Numeric)})
    wrs_row: int = field(metadata={"sa": Column(Numeric)})
    acquisition_year: int = field(metadata={"sa": Column(Numeric)})
    acquisition_month: int = field(metadata={"sa": Column(Numeric)})
    acquisition_day: int = field(metadata={"sa": Column(Numeric)})
    processing_year: int = field(metadata={"sa": Column(Numeric)})
    processing_month: int = field(metadata={"sa": Column(Numeric)})
    processing_day: int = field(metadata={"sa": Column(Numeric)})
    collection_number: int = field(metadata={"sa": Column(Numeric)})
    collection_category: str = field(metadata={"sa": Column(Text)})
    band: int = field(metadata={"sa": Column(Numeric, primary_key=True)})
    project_location_url: str = field(metadata={"sa": Column(Text)})
    platform_id: str = field(metadata={"sa": Column(Text, primary_key=True)})
    status: str = field(default='', metadata={"sa": Column(Text)})
    create_timestamp: datetime = field(default_factory=datetime.now, metadata={"sa": Column(DateTime)})
    last_update_timestamp: datetime = field(default_factory=datetime.now, metadata={"sa": Column(DateTime)})

    @property
    def as_dict(self) -> dict:
        return asdict(self)

    def update(self, engine):
        self.last_update_timestamp = datetime.now()
        engine.session.execute(update(LandsatBandMetadata).where(
            LandsatBandMetadata.platform_id == self.platform_id and LandsatBandMetadata.band == self.band),
                               [self.as_dict])
        engine.session.commit()


def create_from_file_name(file_name, platform_id: str, platform_url: str) -> LandsatBandMetadata | None:
    try:
        params = __name_parser(file_name)
    except AttributeError:
        return None
    if params is not None:
        params.update({'project_location_url': platform_url,
                       'platform_id': platform_id})
        return LandsatBandMetadata(**params)
    else:
        return None


