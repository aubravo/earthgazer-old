import argparse
import json
import logging
import os.path
import pathlib

import numpy as np
from PIL import Image
from matplotlib import pyplot as plt

try:
    import gxiba
    from gxiba.logger import setup_logger
except ModuleNotFoundError:
    from pathlib import Path
    import sys

    root_path = Path(__file__).parents[1]
    sys.path.append(str(root_path))
    import gxiba
    from gxiba.logger import setup_logger

parser = argparse.ArgumentParser()
parser.add_argument('-v', '--verbose', action='store_true', help='Set logging message level to Debug.')
parser.add_argument('-k', '--db-kind', help='Set database kind.', default='sqlite')
parser.add_argument('-H', '--db-host', help='Set database host.')
parser.add_argument('-U', '--db-username', help='Set database username.')
parser.add_argument('-P', '--db-password', help='Set database password.')
parser.add_argument('-p', '--db-port', help='Set database port.')
parser.add_argument('-d', '--db-database', help='Name of the database to use.', default='gxiba')
parser.add_argument('-F', '--db-force-engine', action='store_true', help='Force engine generation.')
parser.add_argument('-K', '--get-keys-from-env', action='store_true',
                    help='Get the Google Service Account keys from environmental variables instead of a keys.json file '
                         'stored in the project path.')
parser.add_argument('-i', '--platform-id', help='Platform id to download. If none provided uses latest.')
parser.add_argument('-B', '--bucket-path', help='Path to bucket.')
parser.add_argument('--skip-sentinel', action='store_true')
parser.add_argument('--skip-landsat', action='store_true')

if __name__ == '__main__':
    # Set up logger
    cli_arguments = parser.parse_args()
    setup_logger()
    logger = logging.getLogger(__name__)
    logger.debug('Logger set up.')
    database_keys = vars(cli_arguments)
    database_keys = {key.replace('db_', ''): database_keys[key] for key in database_keys if 'db_' in key}

    # Set up resource managers
    local_storage = gxiba.LocalEnvironmentManager()
    with open(f'{local_storage.project_path}keys.json') as keys:
        google_keys = json.loads(keys.read())
    db_engine = gxiba.DataBaseEngine(**database_keys)
    cloud_storage = gxiba.CloudStorageManager(gxiba.GoogleCloudStorageInterface, google_keys)

    landsat_image = gxiba.LandsatImage()

    # Get interest platform IDs
    for capture in gxiba.database_get_gxiba_image_metadata(db_engine, gxiba.SatelliteImagePlatform.LANDSAT_8,
                                                           status=gxiba.ImageProcessingStatus.BandMetadataProcessed):
        # Create local platform save path
        local_path = pathlib.Path(f'{local_storage.project_path}/tmp/{capture.platform_id}/')
        local_path.mkdir(exist_ok=True, parents=True)

        # Download and prepare bands images
        for band in gxiba.LandsatInterestBands:

            logger.info(f'Preparing to process {capture.platform_id} band {band.name}: {band.value}')

            # Prepare download
            for band_metadata in gxiba.database_get_landsat_band_metadata_by_platform_id(
                    db_engine, capture.platform_id, band=band.value):
                local_band_save_path = f'{local_path.absolute()}\\{capture.platform_id}_B{band.value}.tif'
                # Download
                if not os.path.exists(local_band_save_path):
                    cloud_storage.download(band_metadata.project_location_url, local_band_save_path)

                # Load image
                band_image = Image.open(local_band_save_path)

                # Load as array and prepare
                band_as_array = np.rint(np.interp(np.array(band_image.getdata()), (0, 65_535), (0, 255))).astype(
                    np.uint8).reshape((band_image.height, band_image.width))
                setattr(landsat_image, band.name, band_as_array)

        # Construct images
        if not landsat_image.is_empty:
            figure, (ax1, ax2) = plt.subplots(1, 2)
            figure.subplots_adjust(bottom=0, top=1, left=0, right=1, hspace=0, wspace=0)
            ax1.imshow(Image.fromarray(landsat_image.rgb_array))
            ax1.set_axis_off()
            ax2.imshow(Image.fromarray(landsat_image.swir_array))
            ax2.set_axis_off()
            plt.margins(0,0)
            plt.savefig(f'{local_path.absolute()}\\{capture.platform_id}_band_comparison.png', transparent=True, bbox_inches="tight", pad_inches=0)
            landsat_image.save_full_exdir(f'{local_path.absolute()}\\{capture.platform_id}.exdir')
