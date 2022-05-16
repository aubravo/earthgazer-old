import os
import re
import numpy as np
from tifffile import imread, imwrite
from google.cloud import storage
from google.oauth2 import service_account

bands = ["B2.TIF", "B3.TIF", "B4.TIF", "B6.TIF", "B7.TIF"]
key_path = "./keys.json"
re_finder = re.compile(r"LANDSAT/(.*)?/")
band_basename = None

credentials = service_account.Credentials.from_service_account_file(
    key_path, scopes=["https://www.googleapis.com/auth/cloud-platform"],
)

storage_client = storage.Client(credentials=credentials, project=credentials.project_id)
gxiba_bucket = storage_client.get_bucket('gxiba-1')


bash_run = os.popen("gsutil ls gs://gxiba-1/LANDSAT").read()
dir_array = re_finder.findall(bash_run)

for directory in dir_array:
    imgs = storage_client.list_blobs(gxiba_bucket)
    for img in imgs:
        if any(band in img.name for band in bands):
            band_img = img.name.split("/")[-1]
            if not band_basename:
                band_basename = band_img[0:band_img.rfind("_") + 1]
            elif band_basename != band_img[0:band_img.rfind("_") + 1]:
                print("ERROR")
            print("Preparing to download {}".format(band_img))
            img.download_to_filename("tmp/{}".format(band_img))
            # img.download_to_filename("tmp/{}".format(band_img), end=0)
            print("Download completed successfully for {}".format(band_img))
            tmp_files = os.listdir("tmp/")
            if all(band_basename + band in tmp_files for band in bands):
                print("READY FOR MERGING {}".format(band_basename))
                rgb = np.dstack((imread("tmp/{}".format(band_basename + bands[2])),
                                 imread("tmp/{}".format(band_basename + bands[1])),
                                 imread("tmp/{}".format(band_basename + bands[0]))))
                imwrite("res/{}RGB.TIF".format(band_basename), rgb)
                rgb = None
                ir = np.dstack((imread("tmp/{}".format(band_basename + bands[4])),
                                imread("tmp/{}".format(band_basename + bands[3])),
                                imread("tmp/{}".format(band_basename + bands[2]))))
                imwrite("res/{}IR.TIF".format(band_basename), ir)
                ir = None
                print("Merged {} successfully".format(band_basename[:-1]))
                for band in bands:
                    os.remove("tmp/{}".format(band_basename + band))
                band_basename = None
