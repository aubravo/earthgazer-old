import os
import re
import numpy as np
from tifffile import imread, imwrite
from google.cloud import storage
from google.oauth2 import service_account
import logging

## For slow upload speed
storage.blob._DEFAULT_CHUNKSIZE = 2097152  # 1024 * 1024 B * 2 = 2 MB
storage.blob._MAX_MULTIPART_SIZE = 2097152  # 2 MB

bands = ["B2.TIF", "B3.TIF", "B4.TIF", "B6.TIF", "B7.TIF"]
key_path = "./keys.json"
re_finder = re.compile(r"LANDSAT/(.*)?/")

credentials = service_account.Credentials.from_service_account_file(
    key_path, scopes=["https://www.googleapis.com/auth/cloud-platform"],
)

storage_client = storage.Client(credentials=credentials, project=credentials.project_id)
gxiba_bucket = storage_client.get_bucket('gxiba-1')

imgs = storage_client.list_blobs(gxiba_bucket, prefix="LANDSAT")
landsat_set = set()

for img in imgs:
    landsat_set.add(re_finder.match(img.name)[0].split("/")[1])

logging.info("{} elements available for processing\n"
             "Starting processing per item".format(len(landsat_set)))

for element in landsat_set:
    element_check = True
    for band in bands:

        blob = gxiba_bucket.blob("LANDSAT/{}/{}_{}".format(element, element, band))
        if not blob.exists():
            logging.warning("No {} on {}".format(band, element))
            logging.info("{} passed because it lacks at least 1 band.".format(element))
            element_check = False
            break
    if element_check:
        logging.info("All bands found for {}, starting download of bands".format(element))
        for band in bands:
            logging.info("Starting download of band: {}".format(band))
            blob = gxiba_bucket.blob("LANDSAT/{}/{}_{}".format(element, element, band))
            blob.download_to_filename("tmp/{}_{}".format(element, band))
            logging.info("Download of band {} completed".format(band))
        logging.info("Download of all bands completed, attempting merges".format(band))
        rgb = np.dstack((imread("tmp/{}_{}".format(element, bands[2])),
                         imread("tmp/{}_{}".format(element, bands[1])),
                         imread("tmp/{}_{}".format(element, bands[0]))))
        imwrite("res/{}_RGB.TIF".format(element), rgb)
        logging.info("RGB image for {} successfully generated, attempting upload to bucket".format(element))
        rgb = None
        blob = gxiba_bucket.blob("res/{}_RGB.TIF".format(element))
        blob.upload_from_filename("res/{}_RGB.TIF".format(element))
        logging.info("RGB image for {} successfully uploaded".format(element))
        ir = np.dstack((imread("tmp/{}_{}".format(element, bands[4])),
                        imread("tmp/{}_{}".format(element, bands[3])),
                        imread("tmp/{}_{}".format(element, bands[2]))))
        imwrite("res/{}_IR.TIF".format(element), ir)
        logging.info("IR image for {} successfully generated, attempting upload to bucket".format(element))
        ir = None
        blob = gxiba_bucket.blob("res/{}_IR.TIF".format(element))
        blob.upload_from_filename("res/{}_IR.TIF".format(element))
        logging.info("IR image for {} successfully uploaded".format(element))
        for band in bands:
            os.remove("tmp/{}_{}".format(element, band))
        os.remove("res/{}_RGB.TIF".format(element))
        os.remove("res/{}_IR.TIF".format(element))
        logging.info("Temporal files for {} successfully removed".format(element))
