import tarfile
import numpy as np
from tifffile import imread, imwrite
from difflib import SequenceMatcher
import os


def landsat_prep(loc):
    file_ = tarfile.TarFile(name=loc, mode='r')

    for i in file_.getnames():
        if "B2" in i:
            blue = i
        elif "B3" in i:
            green = i
        elif "B4" in i:
            red = i
        elif "B5" in i:
            nir = i
        elif "B6" in i:
            swir1 = i
        elif "B7" in i:
            swir2 = i

    for i in [blue, green, red, nir, swir1, swir2]:
        if i is not None:
            pass
        else:
            return None

    match = SequenceMatcher(None, blue, green).find_longest_match(0, len(blue), 0, len(green))
    basename = blue[match.a:match.a+match.size][:-1]

    for i in [blue, green, red, nir, swir1, swir2]:
        file_.extract(i, path="../test/tmp/")

    rgb = np.dstack((imread("./tmp/"+red),
                     imread("./tmp/"+green),
                     imread("./tmp/"+blue)))
    ir = np.dstack((imread("./tmp/"+nir),
                    imread("./tmp/"+swir1),
                    imread("./tmp/"+swir2)))
    imwrite("./results/{}RGB.TIF".format(basename), rgb)
    imwrite("./results/{}IR.TIF".format(basename), ir)


def merge_dir(loc):
    print(loc)
    files = os.listdir(loc)
    print(files)
    for file in files:
        if ".tar" in file:
            print(file)
            landsat_prep(loc+file)


if __name__ == "__main__":
    import sys
    merge_dir(sys.argv[1])
