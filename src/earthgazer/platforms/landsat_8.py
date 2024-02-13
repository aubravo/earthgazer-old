from typing import Dict
from typing import List

from earthgazer.definitions import AtmosphericReferenceLevel
from earthgazer.definitions import RadiometricMeasure
from earthgazer.location import Location
from earthgazer.operations import render_bigquery_template
from earthgazer.platforms import Band
from earthgazer.platforms import Platform


class Landsat_8(Platform):
    name = "LANDSAT_8"
    bigquery_attribute_mapping: Dict = {
        "bigquery_path": "bigquery-public-data.cloud_storage_geo_index.landsat_index",
        "main_id": "scene_id",
        "secondary_id": "product_id",
        "mission_id": "spacecraft_id",
        "sensing_time": "sensing_time",
        "cloud_cover": "cloud_cover",
        "north_lat": "north_lat",
        "south_lat": "south_lat",
        "west_lon": "west_lon",
        "east_lon": "east_lon",
        "base_url": "base_url",
        "mgrs_tile": "NULL",
        "wrs_path": "wrs_path",
        "wrs_row": "wrs_row",
        "data_type": "data_type",
        "extra_filters": 'spacecraft_id = "LANDSAT_8"',
    }
    bands: List = [
        Band(name="B1", description="Coastal aerosol", wavelength=0.443, resolution=30),
        Band(name="B2", description="Blue", wavelength=0.490, resolution=30),
        Band(name="B3", description="Green", wavelength=0.560, resolution=30),
        Band(name="B4", description="Red", wavelength=0.665, resolution=30),
        Band(name="B5", description="NIR", wavelength=0.842, resolution=30),
        Band(name="B6", description="SWIR 1", wavelength=1.610, resolution=30),
        Band(name="B7", description="SWIR 2", wavelength=2.190, resolution=30),
        Band(name="B8", description="Panchromatic", wavelength=0.590, resolution=15),
        Band(name="B9", description="Cirrus", wavelength=1.375, resolution=30),
        Band(name="B10", description="TIRS 1", wavelength=10.900, resolution=100),
        Band(name="B11", description="TIRS 2", wavelength=12.000, resolution=100),
    ]

    def calculate_radiometric_measure(**kwargs) -> str:
        return RadiometricMeasure.DN.value

    def calculate_athmospheric_reference_level(**kwargs) -> str:
        return AtmosphericReferenceLevel.TOA.value


if __name__ == "__main__":
    landsat_8 = Landsat_8()
    popocatepetl = Location(name="Popocatepetl", latitude=123.456, longitude=654.321, description="Volcano in Mexico")
    print(landsat_8.bands)
    print(landsat_8.get_band_by_name("B1").wavelength)
    print(render_bigquery_template(landsat_8, popocatepetl))
