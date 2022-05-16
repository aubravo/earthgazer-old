import os
import rasterio


def sentinel_prep(loc):
    for root, dirs, files in os.walk(loc):
        if "GRANULE" and "IMG_DATA" in root:
            if len(dirs) > 0:
                for directory in dirs:
                    if directory == "R10m":
                        for file in os.listdir("{}/{}/".format(root, directory)):
                            if "B02" in file:
                                blue = "{}/{}/{}".format(root, directory, file)
                            elif "B03" in file:
                                green = "{}/{}/{}".format(root, directory, file)
                            elif "B04" in file:
                                red = "{}/{}/{}".format(root, directory, file)
                    if directory == "R20m":
                        for file in os.listdir("{}/{}/".format(root, directory)):
                            if "B05" in file:
                                vnir1 = "{}/{}/{}".format(root, directory, file)
                            elif "B06" in file:
                                vnir2 = "{}/{}/{}".format(root, directory, file)
                            elif "B07" in file:
                                vnir3 = "{}/{}/{}".format(root, directory, file)
                            elif "B8A" in file:
                                vnir4 = "{}/{}/{}".format(root, directory, file)
                            elif "B11" in file:
                                swir1 = "{}/{}/{}".format(root, directory, file)
                            elif "B12" in file:
                                swir2 = "{}/{}/{}".format(root, directory, file)
                try:
                    return [red, green, blue, vnir1, vnir2, vnir3, vnir4, swir1, swir2]
                except Exception:
                    return None
            elif len(dirs) == 0:
                for file in files:
                    if "B02" in file:
                        blue = "{}/{}".format(root, file)
                    elif "B03" in file:
                        green = "{}/{}".format(root, file)
                    elif "B04" in file:
                        red = "{}/{}".format(root, file)
                    elif "B05" in file:
                        vnir1 = "{}/{}".format(root, file)
                    elif "B06" in file:
                        vnir2 = "{}/{}".format(root, file)
                    elif "B07" in file:
                        vnir3 = "{}/{}".format(root, file)
                    elif "B8A" in file:
                        vnir4 = "{}/{}".format(root, file)
                    elif "B11" in file:
                        swir1 = "{}/{}".format(root, file)
                    elif "B12" in file:
                        swir2 = "{}/{}".format(root, file)
                try:
                    return [red, green, blue, vnir1, vnir2, vnir3, vnir4, swir1, swir2]
                except Exception:
                    print("Error: could not find all files for {}".format(root))
                    return None
            else:
                print("Error while reading file or dir: {}".format(root))
                return None


def merge_dir(location):
    files = os.listdir(location)
    for file in files:
        res = sentinel_prep("{}{}/".format(location, file))
        if res:
            red_band = rasterio.open(res[0], driver='JP2OpenJPEG')
            green_band = rasterio.open(res[1], driver='JP2OpenJPEG')
            blue_band = rasterio.open(res[2], driver='JP2OpenJPEG')
            rgb = rasterio.open('./temp/{}_rgb.tiff'.format(file), 'w', driver='Gtiff',
                                width=red_band.width, height=red_band.height,
                                count=3,
                                crs=red_band.crs,
                                transform=red_band.transform,
                                dtype='uint16')
            rgb.write(red_band.read(1), 1)
            rgb.write(green_band.read(1), 2)
            rgb.write(blue_band.read(1), 3)
            rgb.close()

            vnir1_band = rasterio.open(res[3], driver='JP2OpenJPEG')
            vnir2_band = rasterio.open(res[4], driver='JP2OpenJPEG')
            vnir3_band = rasterio.open(res[5], driver='JP2OpenJPEG')
            ir = rasterio.open('./temp/{}_vnir.tiff'.format(file),
                               'w', driver='Gtiff',
                               width=vnir1_band.width, height=vnir1_band.height,
                               count=3,
                               crs=red_band.crs,
                               transform=vnir1_band.transform,
                               dtype='uint16')
            ir.write(vnir1_band.read(1), 3)
            ir.write(vnir2_band.read(1), 2)
            ir.write(vnir3_band.read(1), 1)
            ir.close()

            vnir4_band = rasterio.open(res[6], driver='JP2OpenJPEG')
            swir1_band = rasterio.open(res[7], driver='JP2OpenJPEG')
            swir2_band = rasterio.open(res[8], driver='JP2OpenJPEG')
            ir = rasterio.open('./temp/{}_swir.tiff'.format(file), 'w', driver='Gtiff',
                               width=vnir4_band.width, height=vnir4_band.height,
                               count=3,
                               crs=red_band.crs,
                               transform=vnir4_band.transform,
                               dtype='uint16')
            ir.write(vnir4_band.read(1), 3)
            ir.write(swir1_band.read(1), 2)
            ir.write(swir2_band.read(1), 1)
            ir.close()


if __name__ == "__main__":
    import sys
    merge_dir(sys.argv[1])
