from dataclasses import dataclass, asdict
import logging

import exdir
import numpy as np

logger = logging.getLogger(__name__)
@dataclass
class LandsatImage:
    blue: np.ndarray = None
    green: np.ndarray = None
    red: np.ndarray = None
    swir1: np.ndarray = None
    swir2: np.ndarray = None

    @property
    def is_empty(self):
        if any([self.blue is not None, self.green is not None, self.red is not None, self.swir1 is not None, self.swir2 is not None]):
            return False
        else:
            return True

    @property
    def as_list(self):
        return [self.blue, self.green, self.red, self.swir1, self.swir2]

    @property
    def as_dict(self):
        return asdict(self)

    @property
    def rgb_array(self):
        if all([self.blue is not None, self.green is not None, self.red is not None]):
            rgb_array = np.array([self.red, self.green, self.blue])
            print(self.red.shape, self.green.shape, self.blue.shape, rgb_array.shape)
            return np.transpose(rgb_array, (1, 2, 0))
        else:
            raise AttributeError(f'Attempted to retrieve LandsatImage.rgb_array but one or more of bands are None: '
                                 f'red: {self.red.size}, green:{self.green.size}, blue:{self.blue.size}')

    @property
    def swir_array(self):
        if all([self.red is not None, self.swir1 is not None, self.swir2 is not None]):
            swir_array = np.array([self.swir1, self.swir2, self.red])
            print(self.swir2.shape, self.swir1.shape, self.red.shape, swir_array.shape)
            return np.transpose(swir_array, (1, 2, 0))
        else:
            raise AttributeError(f'Attempted to retrieve LandsatImage.swir_array but one or more of bands are None: '
                                 f'swir1: {self.swir1.size}, green:{self.swir2.size}, blue:{self.red.size}')

    def save_full_exdir(self, path):
        logger.debug(f'Attempting to save landsat data as exdir in {path}')
        try:
            with exdir.File(path) as landsat_image_exdir:
                band_group = landsat_image_exdir.create_group('bands')
                for band_name in self.as_dict:
                    band_group.require_dataset(band_name, data=self.as_dict[band_name])

        except Exception as e:
            logger.error(e)
            raise RuntimeError(f'Unable to save exdir: {e}')
