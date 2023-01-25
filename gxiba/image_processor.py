"""Image processor.

This module provides an interface for image processing tools to be applied to satellite images.

It uses Pillow as a basis to offer multiple format support."""

import numpy
from PIL import Image


# TODO Implement Image Processor!
# labels: enhancement

class TIFFBandProcessor:
    def __init__(self, image_path):
        self.image_path = image_path
        self.band_image = Image.open(image_path)
        self.band_as_array = numpy.array(self.band_image.getdata())

    @property
    def as_array(self):
        return self.band_as_array

    @property
    def normalized_to_8bits(self):
        return numpy.rint(numpy.interp(self.band_as_array), (0, 65_535), (0, 255)).astype(numpy.uint8).reshape(
            (self.band_image.height, self.band_image.width))
