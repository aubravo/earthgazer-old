from __future__ import annotations

import datetime
import enum
import json
import logging
import re
from pathlib import Path
from typing import ClassVar
from typing import List
from typing import Optional
import uuid

import fsspec
import jinja2
import numpy as np
import rasterio
from google.cloud import bigquery
from google.oauth2 import service_account
from PIL import Image
from pydantic import AnyUrl
from pydantic import Field
from pydantic_settings import BaseSettings
from pydantic_settings import SettingsConfigDict
from sqlalchemy import Boolean
from sqlalchemy import DateTime
from sqlalchemy import Enum
from sqlalchemy import Float
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import create_engine
from sqlalchemy import func
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import MappedAsDataclass
from sqlalchemy.orm import Session
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
from sqlalchemy.orm import scoped_session
from sqlalchemy.orm import sessionmaker

import earthgazer
from earthgazer.exceptions import ConfigFileNotFound

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
queries_dir = Path(__file__).parent.parent / "queries"
sql_environment = jinja2.Environment(loader=jinja2.FileSystemLoader(
    queries_dir, encoding="utf-8"), autoescape=True)


class RadiometricMeasure(enum.Enum):
    RADIANCE = "RADIANCE"
    REFLECTANCE = "REFLECTANCE"
    DN = "DN"


class AtmosphericReferenceLevel(enum.Enum):
    TOA = "TOA"
    BOA = "BOA"


class ProcessingMethod(enum.Enum):
    TRACK = "TRACK"
    BACKUP = "BACKUP"
    CONVERSION = "CONVERSION"
    COMPOSITE = "COMPOSITE"
    NORMALIZATION = "NORMALIZATION"


class Capture(Base):
    __tablename__ = "capture"
    main_id: Mapped[str] = mapped_column(String(30), primary_key=True)
    secondary_id: Mapped[str] = mapped_column(String(30))
    mission_id: Mapped[str] = mapped_column(String(30))
    sensing_time: Mapped[DateTime] = mapped_column(DateTime)
    north_lat: Mapped[float]
    south_lat: Mapped[float]
    west_lon: Mapped[float]
    east_lon: Mapped[float]
    base_url: Mapped[str] = mapped_column(String(250))
    cloud_cover: Mapped[Optional[float]] = mapped_column(Float, default=None)
    mgrs_tile: Mapped[Optional[str]] = mapped_column(String(30), default=None)
    wrs_path: Mapped[Optional[int]] = mapped_column(Integer, default=None)
    wrs_row: Mapped[Optional[int]] = mapped_column(Integer, default=None)
    data_type: Mapped[Optional[str]] = mapped_column(String(30), default=None)
    capture_id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default_factory=lambda: str(uuid.uuid4().hex))
    files: Mapped[List["File"]] = relationship("File", back_populates="capture", default_factory=list,
                                               cascade="all, delete-orphan")

    added_timestamp: Mapped[datetime.datetime] = mapped_column(
        default_factory=datetime.datetime.now)
    last_updated_timestamp: Mapped[datetime.datetime] = mapped_column(default_factory=datetime.datetime.now,
                                                                      onupdate=datetime.datetime.now)
    schema = "earthgazer"

    @classmethod
    def get_by_main_id(cls, session: Session, main_id: str) -> 'Capture' | None:
        return session.query(cls).filter(cls.main_id == main_id).first()


class File(Base):
    __tablename__ = "file"
    capture_id: Mapped[str] = mapped_column(
        ForeignKey("capture.main_id"), nullable=True)
    sub_id: Mapped[str] = mapped_column(String(30), primary_key=True)
    file_format: Mapped[str] = mapped_column(String(30))
    processing_method: Mapped[ProcessingMethod] = mapped_column(
        Enum(ProcessingMethod))
    source_path: Mapped[Optional[str]] = mapped_column(String(250))
    storage_path: Mapped[Optional[str]] = mapped_column(String(250))
    radiometric_measure: Mapped[Optional[str]] = mapped_column(
        Enum(RadiometricMeasure), nullable=True)
    athmospheric_reference_level: Mapped[Optional[str]] = mapped_column(
        Enum(AtmosphericReferenceLevel), nullable=True)
    file_id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default_factory=lambda: str(uuid.uuid4().hex))
    capture: Mapped["Capture"] = relationship(
        'Capture', back_populates='files', default=None)
    sources: Mapped[Optional[List["FileSource"]]] = relationship('FileSource', foreign_keys='FileSource.file_id',
                                                                 back_populates='file', default_factory=list)
    derived_images: Mapped[Optional[List["FileSource"]]] = relationship('FileSource',
                                                                        foreign_keys='FileSource.source_file_id',
                                                                        back_populates='source_file',
                                                                        default_factory=list)
    added_timestamp: Mapped[datetime.datetime] = mapped_column(
        default_factory=datetime.datetime.now)
    last_updated_timestamp: Mapped[datetime.datetime] = mapped_column(default_factory=datetime.datetime.now,
                                                                      onupdate=datetime.datetime.now)
    schema = "earthgazer"


class FileSource(Base):
    __tablename__ = "file_source"
    file_id: Mapped[str] = mapped_column(
        ForeignKey("file.file_id"), primary_key=True)
    source_file_id: Mapped[str] = mapped_column(
        ForeignKey("file.file_id"), default=None, primary_key=True)
    file: Mapped[File] = relationship(
        'File', foreign_keys=[file_id], back_populates='sources', default=None)
    source_file: Mapped[File] = relationship('File', foreign_keys=[
                                             source_file_id], back_populates='derived_images', default=None)
    schema = "earthgazer"


class Location(Base):
    __tablename__ = "location"
    location_id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True)
    location_name: Mapped[str] = mapped_column(String(50))
    location_description: Mapped[Optional[str]] = mapped_column(String(500))
    latitude: Mapped[float] = mapped_column(Float)
    longitude: Mapped[float] = mapped_column(Float)
    active: Mapped[bool] = mapped_column(Boolean, default=True)
    monitoring_period_start: Mapped[Optional[datetime.date]] = mapped_column(
        default=datetime.datetime.fromisoformat("1950-01-01"))
    monitoring_period_end: Mapped[Optional[datetime.date]] = mapped_column(
        default=datetime.date.fromisoformat("2050-12-12"))

    added_timestamp: Mapped[datetime.datetime] = mapped_column(
        default_factory=datetime.datetime.now)
    last_updated_timestamp: Mapped[datetime.datetime] = mapped_column(
        default_factory=datetime.datetime.now, onupdate=datetime.datetime.now)
    schema = "earthgazer"

    def __repr__(self) -> str:
        repr = f"{self.location_id: >4} | {self.location_name:25} | {self.latitude:11.6f} | {self.longitude:11.6f} | " \
               f"{'active' if self.active else 'inactive': >8} | {self.monitoring_period_start} | " \
               f"{self.monitoring_period_end}"
        return repr


class EGConfig(BaseSettings):
    # Data
    force_download: bool = False
    force_get_source_file_data: bool = False
    storage_type: str = Field(default="local")
    local_storage_base_path: str = f"{local_path}/storage"
    cloud_backup_bucket: str = "gxiba-storage"
    remote_storage_base_path: str = f"{cloud_backup_bucket}/eg/storage"
    google_credentials_file_path: str = f"{local_path}/credentials.json"


class BandProcessor:
    """Class for processing band images"""

    @staticmethod
    def open_band(band_path):
        with rasterio.open(band_path) as src:
            return src.read(1)

    @staticmethod
    def save_image(image, output_path):
        image = np.interp(image, (image.min(), image.max()),
                          (0, 255)).astype(np.uint8)
        im = Image.fromarray(image)
        im.save(output_path, "JPEG", quality=100)


class EarthgazerProcessor:
    @staticmethod
    def load_config(config_file: str) -> dict:
        config_path = Path(f"config/{config_file}.json")
        logger.debug(
            f"Loading {config_file} config from {config_path.absolute()}")
        try:
            with config_path.open(encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError as err:
            logger.error(f"{config_file} file not found")
            raise ConfigFileNotFound(f"{config_file} file not found") from err

    def __init__(self, logging_level=logging.INFO):
        logger.setLevel(logging_level)
        self.env = EGConfig()

        service_account_credentials = service_account.Credentials.from_service_account_info(
            json.load(f), scopes=["https://www.googleapis.com/auth/cloud-platform"])

        self.bigquery_client = bigquery.Client(credentials=service_account_credentials,
                                               project=service_account_credentials.project_id)

        # TODO: Add logic to handle multiple types of filesystems
        self.gcs_storage_options = {
            "token": self.env.google_credentials_file_path}
        self.gcs_storage_client = fsspec.filesystem(
            "gcs", **self.gcs_storage_options)

        engine = create_engine(str(self.env.database_url),
                               echo=self.env.database_engine_echo)
        Base.metadata.create_all(engine)
        self.session_factory = sessionmaker(bind=engine)

    def add_location(self, **kwargs):
        session = scoped_session(self.session_factory)
        try:
            location_data = kwargs
            for key in location_data:
                if "monitoring_period" in key:
                    if isinstance(location_data[key], str):
                        location_data[key] = datetime.date.fromisoformat(
                            location_data[key])
            if "location_description" not in location_data:
                location_data["location_description"] = ""
            location_data["location_id"] = session.query(
                func.coalesce(func.max(Location.location_id), 0)).scalar() + 1
            location = Location(**location_data)
            session.add(location)
            session.commit()
        finally:
            session.close()

    def list_locations(self):
        session = scoped_session(self.session_factory)
        try:
            return session.query(Location).all()
        finally:
            session.close()

    def drop_location(self, location_id):
        session = scoped_session(self.session_factory)
        try:
            session.query(Location).filter(
                Location.location_id == location_id).delete()
            session.commit()
        finally:
            session.close()

    def update_bigquery_data(self, logging_level=logging.INFO):
        logger.setLevel(logging_level)
        session = scoped_session(self.session_factory)
        logger.info("Beginning data update process")
        try:
            for platform_config in self.bigquery_platforms_config:
                logger.info(
                    f"Updating {platform_config.capitalize()} platform data")
                print(session.query(Location).where(Location.active))
                for location in session.query(Location).where(Location.active):
                    logger.info(
                        f"Updating {location.location_name.capitalize()} location data")
                    platform_query_params = self.bigquery_platforms_config[platform_config]
                    platform_query_params.update(
                        {
                            "lat": location.latitude,
                            "lon": location.longitude,
                            "start_date": location.monitoring_period_start,
                            "end_date": location.monitoring_period_end,
                        }
                    )
                    logger.debug(f"Query parameters: {platform_query_params}")
                    platform_query = sql_environment.get_template(
                        "bigquery_get_locations.sql").render(**platform_query_params)
                    logger.debug(platform_query)
                    for result in self.bigquery_client.query(platform_query):
                        if session.query(Capture).where(Capture.main_id == result["main_id"]).count() > 0:
                            logger.debug(
                                f"{result['main_id']} already in database")
                            continue
                        logger.debug(f"Adding {result['main_id']} to database")
                        session.add(Capture(**result))
                        session.commit()
        finally:
            session.close()

    def get_source_file_data(self, logging_level=logging.debug):
        logger.setLevel(logging_level)
        blob_finder = re.compile(
            r"^.*?(?:tiles.*?IMG_DATA.*?|/LC0[0-9]_.*?)_(?P<sub_id>B[0-9A]{1,2}|MTL)\.(?P<format>TIF|jp2|txt)$")

        def mission_parse(captured_data_element: Capture) -> str | None:
            if "SENTINEL-2" in captured_data_element.mission_id:
                return "SENTINEL_2"
            elif "LANDSAT_8" in captured_data_element.mission_id:
                return "LANDSAT_8"
            else:
                logger.warning(
                    f"{captured_data_element.mission_id} for {captured_data_element.main_id}"
                    f"is currently not supported")
                return None

        logger.info("Beginning files tracking process")
        session = scoped_session(self.session_factory)
        try:
            for captured_data_element in session.query(Capture).all():
                logger.debug(f"Processing {captured_data_element.main_id}")
                logger.debug(
                    f"{len(captured_data_element.files)} files already downloaded")
                if (mission := mission_parse(captured_data_element)) is None:
                    logger.debug(
                        f"Unable to parse mission for {captured_data_element.main_id}")
                    continue
                if len(captured_data_element.files) < len(self.bands_definition[mission]) or \
                        self.env.force_get_source_file_data:
                    logger.debug("Downloading missing bands")
                    for blob in self.gcs_storage_client.find(f"{captured_data_element.base_url}/"):
                        if blob_finder_result := blob_finder.search(blob):
                            logger.debug(f"Found matching file: {blob}")
                            sub_id, file_format = blob_finder_result.groupdict(
                            )["sub_id"], blob_finder_result.groupdict()["format"]
                            logger.debug(
                                f"Found {sub_id} {file_format} for {captured_data_element.main_id}")
                            already_loaded_files = session.query(File).where(
                                File.capture_id == captured_data_element.main_id).where(File.sub_id == sub_id)
                            if already_loaded_files.count() > 0 and self.env.force_get_source_file_data:
                                # TODO: Test if this works
                                logger.debug(
                                    f"{sub_id} {file_format} for {captured_data_element.main_id} "
                                    f"already in database, but force flag is set")
                                already_loaded_files.delete()
                                session.flush()
                            elif already_loaded_files.count() > 0:
                                logger.debug(
                                    f"{sub_id} {file_format} for {captured_data_element.main_id} already in database")
                                continue
                            file_data = {
                                "capture_id": captured_data_element.main_id,
                                "sub_id": sub_id,
                                "file_format": file_format,
                                "processing_method": ProcessingMethod.TRACK,
                                "source_path": f"gs://{blob}",
                                "storage_path": None
                            }
                            for info_key in ['radiometric_measure', 'athmospheric_reference_level']:
                                if self.platform_config[mission][info_key]['type'] == 'equals':
                                    file_data[info_key] = self.platform_config[mission][info_key]['value']
                                elif self.platform_config[mission][info_key]['type'] == 'evaluate':
                                    template = jinja2.Template(
                                        self.platform_config[mission][info_key]['value'])
                                    rendered_template = template.render(
                                        **captured_data_element.__dict__)
                                    logger.debug(rendered_template)
                                    file_data[info_key] = eval(
                                        rendered_template)
                                else:
                                    raise NotImplementedError(
                                        f"Unknown type {self.platform_config[mission][info_key]['type']} "
                                        f"for {info_key} in {mission} platform config")

                            source_file = File(**file_data)
                            captured_data_element.files.append(source_file)
                            session.commit()
                else:
                    logger.debug(
                        f"Files for {captured_data_element.main_id} already being tracked")
                    continue
        finally:
            session.close()

    def backup_images(self, logging_level=logging.INFO, force=False):
        logger.setLevel(logging_level)
        present_files = self.gcs_storage_client.find(
            f"gs://{self.env.remote_storage_base_path}/")
        session = scoped_session(self.session_factory)
        try:
            for source_file in session.query(File).where(File.processing_method.in_((ProcessingMethod.TRACK,))):
                logger.debug(
                    f"Backing up {source_file.capture_id} {source_file.sub_id} with id {source_file.file_id}")

                backed_up_file = File(
                    capture_id=source_file.capture_id,
                    sub_id=source_file.sub_id,
                    file_format=source_file.file_format,
                    processing_method=ProcessingMethod.BACKUP,
                    source_path=source_file.source_path,
                    storage_path="",
                    radiometric_measure=source_file.radiometric_measure,
                    athmospheric_reference_level=source_file.athmospheric_reference_level,
                    # file_id="", # Generates automatically
                )
                logger.debug(f'File generation: {backed_up_file}')
                backed_up_file_source = FileSource(
                    file_id=backed_up_file.file_id,
                    source_file_id=source_file.file_id
                )
                logger.debug(f'Source generation: {backed_up_file_source}')
                exit()

                # TODO: refactor all of this
                """
                sourcefile_name = source_file.source_image_url.split("/")[-1]
                if f"{self.env.remote_storage_base_path}/{source_file.main_id}/{sourcefile_name}" not in present_files \
                        or force:
                    save_path = f"gs://{self.env.remote_storage_base_path}/{source_file.main_id}/{sourcefile_name}"
                    self.gcs_storage_client.copy(
                        source_file.source_image_url, save_path)
                    session.add(ProcessedFile(
                        main_id=source_file.main_id,
                        format=source_file.format,
                        storage_path=save_path,
                        processing_type=ProcessingType.BACKUP
                    ))
                    session.add(ProcessingRelationships(
                        main_id=source_file.main_id,
                        source_file_id=source_file.file_id
                    ))
                    session.commit()
                else:
                    try:
                        x = session.query(File).join(FileSource, ProcessingRelationships.processing_id ==
                                                     ProcessedFile.processing_id)\
                            .where(ProcessingRelationships.source_file_id == source_file.file_id)\
                            .where(ProcessedFile.main_id == source_file.main_id)\
                            .where(ProcessedFile.processing_type == ProcessingType.BACKUP).all()
                        if len(x) > 1:
                            raise ValueError(
                                f"Multiple backup files for {source_file.main_id} with ID {x.processing_id}.")
                        elif len(x) == 0:
                            raise ValueError(
                                f"No backup files for {source_file.main_id}.")
                        logger.debug(
                            f"{source_file.main_id} already backed up with ID {x[0].processing_id}.")
                    except ValueError as e:
                        logger.error(e)
                        continue"""
        finally:
            session.close()

    def dn_to_toa_reflectance(self, logging_level=logging.INFO):
        logger.setLevel(logging_level)
        logger.debug("Beginning TOA reflectance conversion process")
        session = scoped_session(self.session_factory)
        try:
            ...

        finally:
            session.close()
