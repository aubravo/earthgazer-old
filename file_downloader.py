import datetime
import json
import logging
import os
import re
import shutil
from pathlib import Path
from typing import ClassVar

import jinja2
import numpy as np
import rasterio
from PIL import Image
from google.api_core import retry
from google.cloud import bigquery, storage
from google.oauth2 import service_account
from pydantic import Field, AnyUrl
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy import create_engine, func
from sqlalchemy.exc import NoResultFound, MultipleResultsFound, IntegrityError
from sqlalchemy.orm import scoped_session, sessionmaker

from exceptions import MissingBandError, DuplicateBandError, ConfigFileNotFound

logger = logging.getLogger(__name__)
sql_environment = jinja2.Environment(loader=jinja2.FileSystemLoader('queries/'))

import datetime
import enum

from typing import Optional, List
from sqlalchemy import String, Enum, Integer, Column, Float, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import DeclarativeBase, MappedAsDataclass, Mapped, mapped_column, relationship, Session


class Base(DeclarativeBase, MappedAsDataclass):
    pass

class RadiometricMeasure(enum.Enum):
    RADIANCE = "RADIANCE"
    REFLECTANCE = "REFLECTANCE"
    DN = "DN"


class AtmosphericReferenceLevel(enum.Enum):
    TOA = "TOA"
    BOA = "BOA"


class BandStatus(enum.Enum):
    FOUND = "FOUND"
    STORING_BAND = "STORING_BAND"
    STORED_BAND = "STORED_BAND"
    BAND_STORAGE_FAILED = "BAND_STORAGE_FAILED"


class CaptureData(Base):
    __tablename__ = "capture_data"
    
    main_id: Mapped[str] = mapped_column(String(30), primary_key=True)
    secondary_id: Mapped[str] = mapped_column(String(30))
    mission_id: Mapped[str] = mapped_column(String(30))
    sensing_time: Mapped[DateTime] = mapped_column(DateTime)
    north_lat: Mapped[float]
    south_lat: Mapped[float]
    west_lon: Mapped[float]
    east_lon: Mapped[float]
    base_url: Mapped[str] = mapped_column(String(120))
    cloud_cover: Mapped[Optional[float]] = None
    radiometric_measure: Mapped[Optional[str]]  = mapped_column(Enum(RadiometricMeasure), default=None)
    athmospheric_reference_level: Mapped[Optional[str]] = mapped_column(Enum(AtmosphericReferenceLevel), default=None)
    mgrs_tile: Mapped[Optional[str]] = mapped_column(String(30), default=None)
    wrs_path: Mapped[Optional[int]] = mapped_column(Integer, default=None)
    wrs_row: Mapped[Optional[int]] = mapped_column(Integer, default=None)
    data_type: Mapped[Optional[str]] = mapped_column(String(30), default=None)
    

    # Relationships
    bands: Mapped[Optional[List["Band"]]] = relationship("Band", default_factory=list)
    composites: Mapped[Optional[List["Composite"]]] = relationship("Composite", default_factory=list)
    
    # Templated columns
    added_timestamp: Mapped[datetime.datetime] = mapped_column(default_factory=datetime.datetime.now)
    last_updated_timestamp: Mapped[datetime.datetime] = mapped_column(default_factory=datetime.datetime.now, onupdate=datetime.datetime.now)
    schema = "earthgazer"
    
    @classmethod
    def get_by_main_id(cls, session: Session, main_id: str) -> "CaptureData":
        return session.query(cls).filter(cls.main_id == main_id).first()

    def add_band(self, band: "Band") -> None:
        self.bands.append(band)

    def add_composite(self, composite: "Composite") -> None:
        self.composites.append(composite)


class Band(Base):
    __tablename__ = "band"
    
    image_id: Mapped[str] = mapped_column(String(30), primary_key=True)
    main_id: Mapped[str] = mapped_column(ForeignKey("capture_data.main_id"), primary_key=True)
    band_id: Mapped[str] = mapped_column(String(30), primary_key=True)
    image_url: Mapped[str] = mapped_column(String(120))
    status: Mapped[str] = mapped_column(Enum(BandStatus))
    preprocessed_bands: Mapped[List["PreprocessedBand"]] = relationship("PreprocessedBand")

    # Templated columns
    added_timestamp: Mapped[datetime.datetime] = mapped_column(default_factory=datetime.datetime.now)
    last_updated_timestamp: Mapped[datetime.datetime] = mapped_column(default_factory=datetime.datetime.now, onupdate=datetime.datetime.now)
    schema = "earthgazer"


class Composite(Base):
    __tablename__ = "generated_image"

    main_id: Mapped[str] = mapped_column(ForeignKey("capture_data.main_id"), primary_key=True)
    composite_id: Mapped[str] = mapped_column(String(30), primary_key=True) 
    generated_image_id: Mapped[str] = mapped_column(String(30), primary_key=True)
    local_storage_path: Mapped[str] = mapped_column(String(250))
    remote_storage_path: Mapped[str] = mapped_column(String(250))
    
    # Templated columns
    added_timestamp: Mapped[datetime.datetime] = mapped_column(default_factory=datetime.datetime.now)
    last_updated_timestamp: Mapped[datetime.datetime] = mapped_column(default_factory=datetime.datetime.now, onupdate=datetime.datetime.now)
    schema = "earthgazer"


class PreprocessedBand(Base):
    __tablename__ = "preprocessed_band"

    main_id: Mapped[str] = mapped_column(ForeignKey("capture_data.main_id"), primary_key=True)
    band_id: Mapped[str] = mapped_column(ForeignKey("band.band_id"), primary_key=True)
    preprocessing_id: Mapped[str] = mapped_column(String(30), primary_key=True)
    local_storage_path: Mapped[Optional[str]] = mapped_column(String(250))
    remote_storage_path: Mapped[Optional[str]] = mapped_column(String(250))

    added_timestamp: Mapped[datetime.datetime] = mapped_column(default_factory=datetime.datetime.now)
    last_updated_timestamp: Mapped[datetime.datetime] = mapped_column(default_factory=datetime.datetime.now, onupdate=datetime.datetime.now)
    schema = "earthgazer"


class Location(Base):
    __tablename__ = "location"
    
    location_name: Mapped[str] = mapped_column(String(50))
    location_description: Mapped[str] = mapped_column(String(500))
    latitude: Mapped[float] = mapped_column(Float)
    longitude: Mapped[float] = mapped_column(Float)
    active: Mapped[bool] = mapped_column(Boolean, default=True)
    location_id: int = Column(Integer, primary_key=True, autoincrement=True)
    monitoring_period_start: Mapped[Optional[datetime.date]] = mapped_column(default=datetime.datetime.fromisoformat('1950-01-01'))
    monitoring_period_end: Mapped[Optional[datetime.date]] = mapped_column(default=datetime.date.fromisoformat('2050-12-12'))

    # Templated columns
    added_timestamp: Mapped[datetime.datetime] = mapped_column(default_factory=datetime.datetime.now)
    last_updated_timestamp: Mapped[datetime.datetime] = mapped_column(default_factory=datetime.datetime.now, onupdate=datetime.datetime.now)
    schema = "earthgazer"



class EGConfig(BaseSettings):
    model_config = SettingsConfigDict(env_prefix='eg_')

    # Local environment
    local_path: str = f'{os.path.expanduser("~")}/.eg'.replace('\\', '/')
    
    # Pipeline steps
    update_data: bool = False
    download_band_images: bool = False
    composite_generation: bool = False
    normalize_dataset: bool = False
    track_images: bool = False

    # Data
    force_download: bool = False
    storage_type: str = Field(default='local')
    local_storage_base_path: str = f'{local_path}/storage'
    cloud_backup_bucket: str = 'eg-backup'
    remote_storage_base_path: str = f'{cloud_backup_bucket}/eg/storage'
    google_credentials_file_path: str = f'{local_path}/credentials.json'
    google_storage_downloader_retry_inital: int = 1
    google_storage_downloader_retry_maximum: int = 120
    google_storage_downloader_retry_multiplier: int = 2
    google_storage_downloader_retry_timeout: int = 1200

    # Database
    database_url: AnyUrl = Field(default=f'sqlite:///{local_path}/eg.db', exclude=True)
    database_type: ClassVar[str] = str(database_url).split(':')[0]
    database_engine_echo: bool = False
    
    # Platforms
    monitored_platforms: list = ['LANDSAT_8', 'SENTINEL_2']
    

class BandProcessor:
    @staticmethod
    def open_band(band_path):
        with rasterio.open(band_path) as src:
            return src.read(1)

    @staticmethod
    def save_image(image, output_path):
        image = np.interp(image, (image.min(), image.max()), (0, 255)).astype(np.uint8)
        im = Image.fromarray(image)
        im.save(output_path, 'JPEG', quality=100)


class EGProcessor:
    def __init__(self):
        with open('static/ascii_logo.txt', 'r', encoding='utf-8') as f:
            self.logo = f.read()
        logger.info(self.logo)
        with open('static/short_licence_disclaimer.txt', 'r', encoding='utf-8') as f:
            self.short_licence = f.read()
        logger.info(self.short_licence)

        logger.debug('Loading configuration...')
        self.env = EGConfig()
        dump = '\n'
        for key, value in self.env.model_dump().items():
            dump += f'   {key + ":": <45} {value}\n'
        logger.debug(dump)

        Path(self.env.local_path).mkdir(parents=True, exist_ok=True)
        Path(self.env.local_storage_base_path).mkdir(parents=True, exist_ok=True)

        def load_config(config_file: str) -> dict:
            config_path = os.path.join('config', config_file + '.json')
            try:
                with open(config_path, 'r') as f:
                    return json.load(f)
            except FileNotFoundError:
                logger.error(f'{config_file} file not found')
                raise ConfigFileNotFound(f'{config_file} file not found')

        self.bigquery_platforms_config = load_config('bigquery_platforms')
        self.bands_definition = load_config('bands')
        self.composites_definition = load_config('composites')

        with open(self.env.google_credentials_file_path, 'r') as f:
            service_account_credentials = service_account.Credentials.from_service_account_info(
                json.load(f),
                scopes=["https://www.googleapis.com/auth/cloud-platform"]
            )

        self.bigquery_client = bigquery.Client(
            credentials=service_account_credentials,
            project=service_account_credentials.project_id
        )
        self.storage_client = storage.Client(
            credentials=service_account_credentials,
            project=service_account_credentials.project_id
        )

        self.retry_methodology = retry.Retry(
            initial=self.env.google_storage_downloader_retry_inital,
            maximum=self.env.google_storage_downloader_retry_maximum,
            multiplier=self.env.google_storage_downloader_retry_multiplier,
            timeout=self.env.google_storage_downloader_retry_timeout
        )

        engine = create_engine(str(self.env.database_url), echo=self.env.database_engine_echo)
        Base.metadata.create_all(engine)
        self.session_factory = sessionmaker(bind=engine)

    def add_location(self, **kwargs):
        session = scoped_session(self.session_factory)
        try:
            location_data = kwargs
            for key in location_data:
                if 'monitoring_period' in key:
                    location_data[key] = datetime.date.fromisoformat(location_data[key])
            location_data['location_id'] = session.query(func.coalesce(func.max(Location.location_id),0)).scalar() + 1
            location = Location(**location_data)
            session.add(location)
            session.commit()
        finally:
            session.close()
        
    def update_data(self):
        session = scoped_session(self.session_factory)
        logger.info('Beginning data update process')
        try:
            for platform_config in self.bigquery_platforms_config:
                logger.info(f'Updating {platform_config.capitalize()} platform data')
                for location in session.query(Location).where(Location.active == True):
                    logger.info(f'Updating {location.location_name.capitalize()} location data')
                    platform_query_params = self.bigquery_platforms_config[platform_config]
                    platform_query_params.update(
                        {
                            'lat': location.latitude,
                            'lon': location.longitude,
                            'start_date': location.monitoring_period_start,
                            'end_date': location.monitoring_period_end
                        }
                    )
                    platform_query = sql_environment.get_template('bigquery_get_locations.sql').render(**platform_query_params)
                    logger.info(platform_query)
                    for result in self.bigquery_client.query(platform_query):
                        if session.query(CaptureData).where(CaptureData.main_id == result["main_id"]).count() > 0:
                            logger.debug(f'{result["main_id"]} already in database')
                            continue
                        logger.debug(f'Adding {result["main_id"]} to database')
                        
                        session.add(CaptureData(
                            **result
                        ))
                        session.commit()
        finally:
            session.close()


    def download_band_images(self):
        
        
        
        def parse_url(url):
            re.compile(r'gs://(?P<bucket_name>[^/]+)/(?P<blobs_path_name>.+)')
            return re.match(r'gs://(?P<bucket_name>[^/]+)/(?P<blobs_path_name>.+)', url).groupdict()

        logger.info('Beginning band images download process')
        
        valid_status = ['metadata_loaded']
        if self.env.force_download:
            valid_status.append('downloading')
            logger.info('Including images tagged as downloading in the download process')
        session = scoped_session(self.session_factory)
        try:
            for hyperspectral_image in \
                    session.query(ImageMetadata)\
                            .where(ImageMetadata.status.in_(valid_status))\
                            .where(ImageMetadata.mission_id.in_(self.env.monitored_platforms)).all():
                mission_id = hyperspectral_image.mission_id

                logger.info(f'Downloading {hyperspectral_image.main_id} from {mission_id} mission')

                dir_path = f'{self.env.local_storage_base_path}/{mission_id}/{hyperspectral_image.main_id}'
                os.makedirs(dir_path, exist_ok=True)

                # hyperspectral_image.status = 'downloading'
                # session.commit()

                parsed_url = parse_url(hyperspectral_image.base_url)
                bucket = storage.Bucket(
                    client=self.storage_client,
                    name=parsed_url['bucket_name']
                )

                supported_extensions = "|".join(['tif', 'TIF', 'TIFF', 'jp2'])
                exclude_folders = "|".join(['QI_DATA'])
                bands = list(self.bands_definition[hyperspectral_image.mission_id].keys())
                detection_re = re.compile(
                    f"^(?!.*\\b(?:{exclude_folders})\\b).*(_({'|'.join(bands)})\\.({supported_extensions})).*$"
                )
                hits = []
                for blob in bucket.list_blobs(prefix=parsed_url['blobs_path_name'], retry=self.retry_methodology):
                    if detection_re.search(blob.name):
                        logger.debug(f'Found {blob.name}')
                        hits.append(blob)

                        band = detection_re.search(blob.name).group(2)

                        if session.query(BandMetadata).where(BandMetadata.main_id == hyperspectral_image.main_id).where(BandMetadata.band_id == band).count() > 0:
                            band_metadata = session.query(BandMetadata).where(BandMetadata.main_id == hyperspectral_image.main_id).where(BandMetadata.band_id == band).first()
                            if band_metadata.status == 'band_downloaded':
                                logger.debug(f'Band {band} already downloaded for {hyperspectral_image.main_id}')
                                continue
                            elif band_metadata.status == 'metadata_loading':
                                logger.debug(f'Band {band} already in metadata loading state for {hyperspectral_image.main_id}')
                            else:
                                logger.warning(f'{band_metadata.status} status for {hyperspectral_image.main_id}')
                        else:
                            band_metadata = BandMetadata(main_id=hyperspectral_image.main_id,
                                         band_id=band,
                                         image_id=blob.name.split('/')[-1],
                                         status='metadata_loading',
                                         image_url=f'{parsed_url["bucket_name"]}/{blob.name}',
                                         band_metadata=hyperspectral_image)
                            session.add(band_metadata)
                            session.commit()

                        if self.env.save_locally:
                            logger.debug(f'Downloading {blob.name} to {dir_path}/{band_metadata.image_id}')
                            blob.download_to_filename(f'{dir_path}/{band_metadata.image_id}',
                                                      retry=retry_methodology)

                        band_metadata.status = 'band_downloaded'
                        session.commit()

                logger.info(f'Found {len(hits)} matching blobs')
                if len(hits) == 0:
                    logger.warning(f'No hits found for {hyperspectral_image.main_id}')
                    hyperspectral_image.status = 'no_hits'
                    session.commit()

                hyperspectral_image.status = 'downloaded'
                session.commit()
        finally:
            session.close()


    def generate_composites(self):
        logger.info('Beginning composite generation process')
        composite_storage_path = self.env.local_storage_base_path





def main():
    eg = EGProcessor()
    if eg.env.update_data:
        eg.update_data()
    if eg.env.download_band_images:
        eg.download_band_images()
    if eg.env.generate_composites:
        eg.generate_composites()
    exit(0)
    
    # TODO: reimplement this into the EGProcessor class

    with Session(engine) as session:
        if env.composite_generation:
            logger.info('Composite generation')
            os.makedirs('D:/composites', exist_ok=True)

            def filter_images(bands):
                return [filtered_band for filtered_band in bands if
                        '_B' in filtered_band.image_url and
                        'QI_DATA' not in filtered_band.image_url and 'QA' not in filtered_band.image_url]

            for hyperspectral_image in session.query(ImageMetadata).where(
                    ImageMetadata.status.in_(['downloaded', 'generating_composites'])).all():
                hyperspectral_image.status = 'generating_composites'
                session.commit()
                try:
                    interest_bands = filter_images(hyperspectral_image.images)
                    logger.debug(
                        f'{hyperspectral_image.mission_id} - {hyperspectral_image.main_id}:'
                        f' {len(interest_bands)} bands found')

                    if hyperspectral_image.mission_id.lower() in bands_definition.keys():
                        logger.debug(f'Found definition for {hyperspectral_image.mission_id}')
                        for composite_key in composites_definition[hyperspectral_image.mission_id.lower()].keys():
                            composite = []
                            for composite_band in \
                                    composites_definition[hyperspectral_image.mission_id.lower()][composite_key]:
                                x = [band for band in interest_bands if composite_band in band.image_url]
                                if len(x) == 1:
                                    composite.append(x[0])
                                elif len(x) == 0:
                                    raise MissingBandError(f'No band found for {composite_band}')
                                else:
                                    raise DuplicateBandError(f'More than one band found for {composite_band}')

                            logger.debug(f'Composite {composite_key} bands found{[x.image_id for x in composite]}')

                            composite_bands = [
                                BandProcessor.open_band(f'D:/{hyperspectral_image.main_id}/{band.image_id}')
                                for band in composite
                            ]
                            image = np.stack(
                                (composite_bands[1], composite_bands[2], composite_bands[3]),
                                axis=0
                            )
                            image = np.moveaxis(image, 0, -1)
                            BandProcessor.save_image(
                                image,
                                f'D:/composites/{composite[0].image_id[0:composite[0].image_id.rfind("_")]}'
                                f'_{composite_key}.jpg'
                            )

                except (MissingBandError, DuplicateBandError) as e:
                    hyperspectral_image.status = 'composite_generation_error'
                    session.commit()
                    logger.exception(e)
                    continue
                hyperspectral_image.status = 'composite_generated'
                session.commit()

    if env.normalize_dataset:
        logger.info('Normalizing dataset')
        os.makedirs('D:/normalized', exist_ok=True)

        for image in os.listdir('D:/composites'):
            logger.debug(f'Normalizing {image}')
            img = Image.open(f'D:/composites/{image}')
            img = img.resize((256, 256))
            img.save(f'D:/normalized/{image}')



    logger.debug('Ending db session')


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG, format='[%(levelname)s] - %(asctime)s - %(message)s')
    eg = EGProcessor()
    if False:
        import os
        with open(os.path.curdir + '/test/popocatepetl.json', 'r') as f:
            test = json.load(f)
        eg.add_location(**test)
    eg.update_data()
