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
from pydantic import AnyUrl, Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy import create_engine
from sqlalchemy.exc import NoResultFound, MultipleResultsFound, IntegrityError
from sqlalchemy.orm import scoped_session, sessionmaker

from db_config import Image, Location, Band, Base
from exceptions import MissingBandError, DuplicateBandError, ConfigFileNotFound

logger = logging.getLogger(__name__)
sql_environment = jinja2.Environment(loader=jinja2.FileSystemLoader('queries/'))


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

    # TODO: refactor storage to use driver pattern
    # Download/Storage
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
    
    # Locations
    load_locations_from_path: bool = False
    locations_path: str = f'{local_path}/locations'

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
        Path(self.env.locations_path).mkdir(parents=True, exist_ok=True)
        Path(self.env.local_storage_base_path).mkdir(parents=True, exist_ok=True)
        shutil.copyfile('test/popocatepetl.json', f'{self.env.locations_path}/popocatepetl.json')

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

        engine = create_engine(str(self.env.database_url), echo=self.env.database_engine_echo)
        Base.metadata.create_all(engine)
        self.session_factory = sessionmaker(bind=engine)
        session = scoped_session(self.session_factory)
        try:
            if self.env.load_locations_from_path:
                for file in os.listdir(self.env.locations_path):
                    logger.debug('Loading location from path')
                    if file.endswith('.json'):
                        logger.debug(f'Found {file}')
                        with open(os.path.join(self.env.locations_path, file), 'r') as f:
                            loc = json.load(f)
                            loc.update({'start_date': datetime.date.fromisoformat(loc['start_date']),
                                        'end_date': datetime.date.fromisoformat(loc['end_date'])})
                            loc['location_id'] = session.query(Location).count() + 1
                            logger.debug(f'Adding {loc}')
                            try:
                                session.add(Location(**loc))
                                session.commit()
                            except IntegrityError:
                                logger.warning(f'Location {loc["location_name"]} already exists')
                                logger.warning('Rolling back and proceeding.')
                                session.rollback()
                                continue
        finally:
            session.close()

    def update_data(self):
        session = scoped_session(self.session_factory)
        logger.info('Beginning data update process')
        try:
            for platform_config in self.bigquery_platforms_config:
                logger.info(f'Updating {platform_config.capitalize()} platform data')
                for location in session.query(Location).where(Location.active):
                    logger.info(f'Updating {location.location_name.capitalize()} location data')
                    platform_query_params = self.bigquery_platforms_config[platform_config]
                    platform_query_params.update(
                        {
                            'lat': location.latitude,
                            'lon': location.longitude,
                            'start_date': location.monitoring_period_start,
                            'end_date': location.monitoring_period_start
                        }
                    )
                    platform_query = sql_environment.get_template('bigquery_get_locations.sql').render(**platform_query_params)
                    for result in self.bigquery_client.query(platform_query):
                        if session.query(ImageMetadata).where(ImageMetadata.main_id == result["main_id"]).count() > 0:
                            logger.debug(f'{result["main_id"]} already in database')
                            continue
                        logger.debug(f'Adding {result["main_id"]} to database')
                        session.add(ImageMetadata(
                            main_id=result["main_id"],
                            secondary_id=result["secondary_id"],
                            mission_id=result["mission_id"],
                            sensing_time=result["sensing_time"],
                            cloud_cover=result["cloud_cover"],
                            north_lat=result["north_lat"],
                            south_lat=result["south_lat"],
                            west_lon=result["west_lon"],
                            east_lon=result["east_lon"],
                            base_url=result["base_url"],
                            status='metadata_loaded'
                        ))
                        session.commit()
        finally:
            session.close()

    def download_band_images(self):
        def parse_url(url):
            re.compile(r'gs://(?P<bucket_name>[^/]+)/(?P<blobs_path_name>.+)')
            return re.match(r'gs://(?P<bucket_name>[^/]+)/(?P<blobs_path_name>.+)', url).groupdict()

        logger.info('Beginning band images download process')
        retry_methodology = retry.Retry(
            initial=self.env.google_storage_downloader_retry_inital,
            maximum=self.env.google_storage_downloader_retry_maximum,
            multiplier=self.env.google_storage_downloader_retry_multiplier,
            timeout=self.env.google_storage_downloader_retry_timeout
        )
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
                for blob in bucket.list_blobs(prefix=parsed_url['blobs_path_name'], retry=retry_methodology):
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
    main()
