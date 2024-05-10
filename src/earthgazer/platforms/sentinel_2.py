from typing import ClassVar

from earthgazer.exceptions import PlatformAttributeCalculationException
from earthgazer.platforms import AtmosphericReferenceLevel, Band, Platform, RadiometricMeasure


class Sentinel_2(Platform):
    name = "SENTINEL_2"
    bigquery_attribute_mapping: ClassVar[dict] = {
        "bigquery_path": "bigquery-public-data.cloud_storage_geo_index.sentinel_2_index",
        "main_id": "product_id",
        "secondary_id": "granule_id",
        "mission_id": "CASE WHEN product_id LIKE 'S2A%' THEN \"SENTINEL-2A\" WHEN product_id LIKE 'S2B%' "
        'THEN "SENTINEL-2B" ELSE "SENTINEL-2" END',
        "sensing_time": "sensing_time",
        "cloud_cover": "cloud_cover",
        "north_lat": "north_lat",
        "south_lat": "south_lat",
        "west_lon": "west_lon",
        "east_lon": "east_lon",
        "base_url": "base_url",
        "mgrs_tile": "mgrs_tile",
        "wrs_path": "NULL",
        "wrs_row": "NULL",
        "data_type": "NULL",
        "extra_filters": "--",
    }
    bands: ClassVar[list[Band]] = [
        Band(name="B01", description="Coastal aerosol", wavelength=0.443, resolution=60),
        Band(name="B02", description="Blue", wavelength=0.490, resolution=10),
        Band(name="B03", description="Green", wavelength=0.560, resolution=10),
        Band(name="B04", description="Red", wavelength=0.665, resolution=10),
        Band(name="B05", description="Red edge 1", wavelength=0.705, resolution=20),
        Band(name="B06", description="Red edge 2", wavelength=0.740, resolution=20),
        Band(name="B07", description="Red edge 3", wavelength=0.783, resolution=20),
        Band(name="B08", description="NIR", wavelength=0.842, resolution=10),
        Band(name="B8A", description="NIR", wavelength=0.865, resolution=20),
        Band(name="B09", description="Water vapour", wavelength=0.945, resolution=60),
        Band(name="B10", description="SWIR - Cirrus", wavelength=1.375, resolution=60),
        Band(name="B11", description="SWIR 1", wavelength=1.610, resolution=20),
        Band(name="B12", description="SWIR 2", wavelength=2.190, resolution=20),
    ]

    def calculate_radiometric_measure(self, **kwargs) -> str:
        return RadiometricMeasure.REFLECTANCE.value

    def calculate_athmospheric_reference_level(self, main_id: str, **kwargs) -> str:
        if "_MSIL1C_" in main_id:
            return AtmosphericReferenceLevel.TOA.value
        elif "_MSIL2A_" in main_id:
            return AtmosphericReferenceLevel.BOA.value
        else:
            raise PlatformAttributeCalculationException(f"Unable to calculate Athmospheric Reference Level from main_id {main_id}")
