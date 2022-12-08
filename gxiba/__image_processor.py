"""Image processor.

This module provides an interface for image processing tools to be applied to satellite images.

It uses Pillow as a basis to offer multiple format.
"""

from PIL import Image


class ImageProcessor:
    def __init__(self):
        self.test = None

    def test(self):
        return self.test()


if __name__ == '__main__':
    x = ImageProcessor()
