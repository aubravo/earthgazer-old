"""Earthgazer platforms module.
This module includes the abstract Platform and Band classes, which are used to define the different satellite platforms and their respective bands.
"""

import enum
from abc import ABC, abstractmethod
from pathlib import Path

import jinja2

from earthgazer.location import Location


class RadiometricMeasure(enum.Enum):
    RADIANCE = "RADIANCE"
    REFLECTANCE = "REFLECTANCE"
    DN = "DN"


class AtmosphericReferenceLevel(enum.Enum):
    TOA = "TOA"
    BOA = "BOA"


class Band:
    """Band class.
    This class is used to define the different bands of a satellite platform.
    """

    def __init__(self, name: str, description: str | None, wavelength: float | None, resolution: float | None):
        self.name = name
        self.description = description
        self.wavelength = wavelength
        self.resolution = resolution

    def __repr__(self):
        return f"{self.name}({self.description})"


class Platform(ABC):
    """Platform class.
    This Abstract class is used to define the different satellite platforms.
    """

    name: str
    bigquery_attribute_mapping: dict
    bands: list[Band]
    athmospheric_reference_level: str

    def get_band_by_name(self, name: str) -> Band:
        for band in self.bands:
            if band.name == name:
                return band
        raise ValueError(f"Band {name} not found in {self.name}")

    @abstractmethod
    def calculate_radiometric_measure(**kwargs) -> RadiometricMeasure:
        """This method is used to calculate the radiometric measure specific to the platform.

        :return: The radiometric measure type.
        :rtype: earthgazer.definitions.RadiometricMeasure
        """
        ...

    @abstractmethod
    def calculate_athmospheric_reference_level(**kwargs) -> AtmosphericReferenceLevel:
        """_summary_

        :return: _description_
        :rtype: earthgazer.definitions.AtmosphericReferenceLevel
        """
        ...

    def render_bigquery_template(self, location: Location):
        queries_dir = Path(__file__).parent.parent / "queries"
        sql_environment = jinja2.Environment(loader=jinja2.FileSystemLoader(queries_dir, encoding="utf-8"), autoescape=True)
        mappings = {}
        mappings.update(self.bigquery_attribute_mapping)
        mappings.update(location.model_dump())
        return sql_environment.get_template("bigquery_get_locations.sql").render(**mappings)
