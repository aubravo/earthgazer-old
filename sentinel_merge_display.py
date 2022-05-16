"""
Este código recupera las imágenes descargadas de la base de datos de Sentinel
y las une para generar imágenes RGB, VNIR y SWIR y hacer display por medio de
pyplot
"""

import rasterio
from rasterio.plot import show
import matplotlib.pyplot as plt


frame = "0005a38b-c525-4c83-aaee-f8e5cfd5d69e"
location = "./temp/0005a38b-c525-4c83-aaee-f8e5cfd5d69e/" \
           "S2A_MSIL2A_20210615T165851_N0300_R069_T14QNF_20210615T212307.SAFE/" \
           "GRANULE/" \
           "L2A_T14QNF_A031240_20210615T170711/" \
           "IMG_DATA/" \
           "R60m/T14QNF_20210615T165851_{}_60m.jp2"

bands = ["./temp/{}_rgb.tiff".format(frame),
         "./temp/{}_vnir.tiff".format(frame),
         "./temp/{}_swir.tiff".format(frame)]


for i in ["B01", "B02", "B03", "B04", "B04", "B06", "B07", "B8A", "B09", "B11", "B12"]:
    bands.append(location.format(i))
    print(bands[-1])

width = 4
height = 3
offset = 3
titles = ["Espectro Visible", "VNIR", "SWIR",
          "B1 - 443nm", "B2 - 490nm", "B3 - 560nm", "B4 - 665nm",
          "B5 - 705nm", "B6 - 740nm", "B7 - 783nm", "B8A - 865nm",
          "B9 - 940nm", "B11 - 1610nm", "B12 - 2190"]

fig, axis = plt.subplots(height, width)
# for i in range (0, 3):
for i in range(3, len(bands)):
    raster = rasterio.open(bands[i]).read()
    raster = (raster-raster.min())/(raster.max()-raster.min())
    #axis[i].set_axis_off()
    # show(raster, ax=axis[i], title=titles[i])
    axis[(i - offset) // width, (i - offset) % width].set_axis_off()
    show(raster, ax=axis[(i - offset) // width, (i - offset) % width],  title=titles[i])

axis[2, 3].set_visible(False)

plt.show()
