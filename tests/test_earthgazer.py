import pathlib
import sys
import unittest

import pytest
from pydantic import ValidationError

from earthgazer.exceptions import PlatformAttributeCalculationException
from earthgazer.platforms.landsat_8 import Landsat_8
from earthgazer.platforms.sentinel_2 import Sentinel_2
from earthgazer.settings import EarthGazerSettings


sys.path.append(f"{pathlib.Path(__file__).parent.parent}\\src\\")
print(sys.path)
from earthgazer.location import Location  # noqa: E402


class EarthGazerSettingsTest(unittest.TestCase):
    def test_working_path(self):
        earthgazer_settings = EarthGazerSettings()
        assert earthgazer_settings.config_path == str(pathlib.Path.home() / "etc/.eg")
        assert pathlib.Path(earthgazer_settings.config_path).exists()
    
    def test_database_validation(self):
        earthgazer_settings = EarthGazerSettings()
        assert earthgazer_settings.database_manager.drivername == "postgresql+psycopg2"
        assert earthgazer_settings.database_manager.username == "earthgazer-user"
        assert earthgazer_settings.database_manager.password == "earthgazer-password"
        assert earthgazer_settings.database_manager.host == "localhost"
        assert earthgazer_settings.database_manager.port == 5432
        assert earthgazer_settings.database_manager.database == "earthgazer-test"
        assert earthgazer_settings.database_manager.echo_sql is False


class PlatformTestSentinel2(unittest.TestCase):
    def test_band(self):
        sentinel_2 = Sentinel_2()
        assert sentinel_2.get_band_by_name("B01") == sentinel_2.bands[0]
        assert sentinel_2.get_band_by_name("B01").description == "Coastal aerosol"
        assert sentinel_2.get_band_by_name("B01").wavelength == 0.443
        assert sentinel_2.get_band_by_name("B01").resolution == 60
        assert repr(sentinel_2.bands[0]) == "B01(Coastal aerosol)"
        with pytest.raises(ValueError, match="Band B1 not found in SENTINEL_"):
            sentinel_2.get_band_by_name("B1")

    def test_calculate_radiometric_measure(self):
        sentinel_2 = Sentinel_2()
        assert sentinel_2.calculate_radiometric_measure() == "REFLECTANCE"

    def test_calculate_athmospheric_reference_level(self):
        sentinel_2 = Sentinel_2()
        assert sentinel_2.calculate_athmospheric_reference_level("S2A_MSIL1C_20210101T123456_N0209_R123_T30TWM_20210101T123456") == "TOA"
        assert sentinel_2.calculate_athmospheric_reference_level("S2A_MSIL2A_20210101T123456_N0209_R123_T30TWM_20210101T123456") == "BOA"

        with pytest.raises(PlatformAttributeCalculationException):
            sentinel_2.calculate_athmospheric_reference_level("S2A_MSIL3C_20210101T123456_N0209_R123_T30TWM_20210101T123456")

    def test_rendered_bigquery_template(self):
        sentinel_2 = Sentinel_2()
        location = Location(
            name="Popocatepetl",
            latitude=19.0224,
            longitude=98.6279,
            description="Volcano in Mexico",
            monitoring_start="2021-01-01",
            monitoring_end="2021-12-31",
        )
        assert sentinel_2.render_bigquery_template(location) == """SELECT
    product_id AS main_id,
    granule_id AS secondary_id,
    CASE WHEN product_id LIKE 'S2A%' THEN "SENTINEL-2A" WHEN product_id LIKE 'S2B%' THEN "SENTINEL-2B" ELSE "SENTINEL-2" END AS mission_id,
    sensing_time AS sensing_time,
    cloud_cover AS cloud_cover,
    north_lat AS north_lat,
    south_lat AS south_lat,
    west_lon AS west_lon,
    east_lon AS east_lon,
    base_url AS base_url,
    mgrs_tile AS mgrs_tile,
    NULL AS wrs_path,
    NULL AS wrs_row,
    NULL AS data_type
FROM bigquery-public-data.cloud_storage_geo_index.sentinel_2_index
WHERE
    sensing_time >= '2021-01-01' AND
    sensing_time <= '2021-12-31' AND
    -- AND
    north_lat >= 19.0224 AND
    south_lat <= 19.0224 AND
    west_lon <= 98.6279 AND
    east_lon >= 98.6279"""


class PlatformTestLandsat8(unittest.TestCase):
    def test_band(self):
        landsat_8 = Landsat_8()
        assert landsat_8.get_band_by_name("B1") == Landsat_8.bands[0]
        assert landsat_8.get_band_by_name("B1").description == "Coastal aerosol"
        assert landsat_8.get_band_by_name("B1").wavelength == 0.443
        assert landsat_8.get_band_by_name("B1").resolution == 30
        assert repr(landsat_8.bands[0]) == "B1(Coastal aerosol)"
        with pytest.raises(ValueError, match="Band B01 not found in LANDSAT_8"):
            landsat_8.get_band_by_name("B01")

    def test_calculate_radiometric_measure(self):
        landsat_8 = Landsat_8()
        assert landsat_8.calculate_radiometric_measure() == "DN"

    def test_calculate_athmospheric_reference_level(self):
        landsat_8 = Landsat_8()
        assert landsat_8.calculate_athmospheric_reference_level() == "TOA"

    def test_rendered_bigquery_template(self):
        landsat_8 = Landsat_8()
        location = Location(
            name="Popocatepetl",
            latitude=19.0224,
            longitude=98.6279,
            description="Volcano in Mexico",
            monitoring_start="2021-01-01",
            monitoring_end="2021-12-31",
        )
        assert landsat_8.render_bigquery_template(location) == """SELECT
    scene_id AS main_id,
    product_id AS secondary_id,
    spacecraft_id AS mission_id,
    sensing_time AS sensing_time,
    cloud_cover AS cloud_cover,
    north_lat AS north_lat,
    south_lat AS south_lat,
    west_lon AS west_lon,
    east_lon AS east_lon,
    base_url AS base_url,
    NULL AS mgrs_tile,
    wrs_path AS wrs_path,
    wrs_row AS wrs_row,
    data_type AS data_type
FROM bigquery-public-data.cloud_storage_geo_index.landsat_index
WHERE
    sensing_time >= '2021-01-01' AND
    sensing_time <= '2021-12-31' AND
    spacecraft_id = "LANDSAT_8" AND
    north_lat >= 19.0224 AND
    south_lat <= 19.0224 AND
    west_lon <= 98.6279 AND
    east_lon >= 98.6279"""


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
                latitude=self.location_latitude,
                longitude=self.location_longitude + 180,
                description=self.description,
                monitoring_start=self.monitoring_start,
                monitoring_end=self.monitoring_end,
            )
        with pytest.raises(ValueError, match="month must be in 1..12"):
            Location(
                name=self.location_name,
                latitude=self.location_latitude,
                longitude=self.location_longitude,
                description=self.description,
                monitoring_start="2021-13-01",
                monitoring_end=self.monitoring_end,
            )
        with pytest.raises(ValueError, match="day is out of range for month"):
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
