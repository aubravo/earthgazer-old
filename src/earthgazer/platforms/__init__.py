from abc import ABC
from typing import List
from typing import Optional


class Band:
    def __init__(self, name: str,
                 description: Optional[str],
                 wavelength: Optional[float],
                 resolution: Optional[float]):
        self.name = name
        self.description = description
        self.wavelength = wavelength
        self.resolution = resolution

    def __repr__(self):
        return self.name


class Platform(ABC):
    NAME: str
    BANDS: List[Band]

    def get_band_by_name(self, name: str) -> Band:
        for band in self.BANDS:
            if band.name == name:
                return band
        raise ValueError(f"Band {name} not found in {self.NAME}")
