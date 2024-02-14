import pathlib
import sys
import unittest

sys.path.append(f"{pathlib.Path(__file__).parent.parent}\\src\\")
print(sys.path)
from earthgazer.location import Location  # noqa: E402


class LocationTest(unittest.TestCase):
    location_name = "Popocatepetl"
    location_latitude = 19.0224
    location_longitude = 98.6279
    description = "Volcano in Mexico"
    monitoring_start = "2021-01-01"
    monitoring_end = "2021-12-31"

    @unittest.expectedFailure
    def test_invalid_latitude(self):
        Location(
            name=self.location_name,
            latitude=self.location_latitude + 180,
            longitude=self.location_longitude,
            description=self.description,
            monitoring_start=self.monitoring_start,
            monitoring_end=self.monitoring_end,
        )

    @unittest.expectedFailure
    def test_invalid_longitude(self):
        Location(
            name=self.location_name,
            latitude=self.location_latitude,
            longitude=self.location_longitude + 180,
            description=self.description,
            monitoring_start=self.monitoring_start,
            monitoring_end=self.monitoring_end,
        )

    @unittest.expectedFailure
    def test_invalid_monitoring_start(self):
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
