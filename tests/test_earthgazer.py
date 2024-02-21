import pathlib
import sys
import unittest

import pytest
from pydantic import ValidationError

from earthgazer.exceptions import PlatformAttributeCalculationException
from earthgazer.platforms.sentinel_2 import Sentinel_2

sys.path.append(f"{pathlib.Path(__file__).parent.parent}\\src\\")
print(sys.path)
from earthgazer.location import Location  # noqa: E402


class PlatformTest(unittest.TestCase):
    def test_get_band_by_name(self):
        sentinel_2 = Sentinel_2()
        assert sentinel_2.get_band_by_name("B01") == sentinel_2.bands[0]
        assert sentinel_2.get_band_by_name("B01").description == "Coastal aerosol"
        assert sentinel_2.get_band_by_name("B01").wavelength == 0.443
        assert sentinel_2.get_band_by_name("B01").resolution == 60

    def test_calculate_radiometric_measure(self):
        sentinel_2 = Sentinel_2()
        assert sentinel_2.calculate_radiometric_measure() == "REFLECTANCE"

    def test_calculate_athmospheric_reference_level(self):
        sentinel_2 = Sentinel_2()
        assert sentinel_2.calculate_athmospheric_reference_level("S2A_MSIL1C_20210101T123456_N0209_R123_T30TWM_20210101T123456") == "TOA"
        assert sentinel_2.calculate_athmospheric_reference_level("S2A_MSIL2A_20210101T123456_N0209_R123_T30TWM_20210101T123456") == "BOA"

        with pytest.raises(PlatformAttributeCalculationException):
            sentinel_2.calculate_athmospheric_reference_level("S2A_MSIL3C_20210101T123456_N0209_R123_T30TWM_20210101T123456")


class LocationTest(unittest.TestCase):
    location_name = "Popocatepetl"
    location_latitude = 19.0224
    location_longitude = 98.6279
    description = "Volcano in Mexico"
    monitoring_start = "2021-01-01"
    monitoring_end = "2021-12-31"

    def test_validation_errors(self):
        with pytest.raises(ValidationError):
            Location(
                name=self.location_name,
                latitude=self.location_latitude + 180,
                longitude=self.location_longitude,
                description=self.description,
                monitoring_start=self.monitoring_start,
                monitoring_end=self.monitoring_end,
            )
        with pytest.raises(ValidationError):
            Location(
                name=self.location_name,
                latitude=self.location_latitude + 180,
                longitude=self.location_longitude,
                description=self.description,
                monitoring_start=self.monitoring_start,
                monitoring_end=self.monitoring_end,
            )
        with pytest.raises(ValidationError):
            Location(
                name=self.location_name,
                latitude=self.location_latitude,
                longitude=self.location_longitude,
                description=self.description,
                monitoring_start="2021-13-01",
                monitoring_end=self.monitoring_end,
            )

    @unittest.expectedFailure
    def test_invalid_monitoring_end(self):
        Location(
            name=self.location_name,
            latitude=self.location_latitude,
            longitude=self.location_longitude,
            description=self.description,
            monitoring_start=self.monitoring_start,
            monitoring_end="2021-12-32",
        )

    def test_location_as_dict(self):
        location = Location(
            name=self.location_name,
            latitude=self.location_latitude,
            longitude=self.location_longitude,
            description=self.description,
            monitoring_start=self.monitoring_start,
            monitoring_end=self.monitoring_end,
        )
        assert location.model_dump() == {
            "name": self.location_name,
            "latitude": self.location_latitude,
            "longitude": self.location_longitude,
            "description": self.description,
            "monitoring_start": self.monitoring_start,
            "monitoring_end": self.monitoring_end,
        }


if __name__ == "__main__":
    unittest.main()
