from datetime import date


class Location:
    def __init__(
        self,
        name: str,
        latitude: float,
        longitude: float,
        description: str | None = "",
        monitoring_start: str | None = "1990-01-01",
        monitoring_end: str | None = "2050-01-01",
    ):
        self.name = name
        self.latitude = latitude
        self.longitude = longitude
        self.description = description
        date.fromisoformat(monitoring_start)
        date.fromisoformat(monitoring_end)
        self.monitoring_start = monitoring_start
        self.monitoring_end = monitoring_end

    def __repr__(self) -> str:
        return f"{self.name} ({self.latitude},{self.longitude}) - {self.description}"

    @property
    def as_dict(self):
        return {
            "location_name": self.name,
            "location_latitude": self.latitude,
            "location_longitude": self.longitude,
            "location_description": self.description,
            "location_monitoring_start": self.monitoring_start,
            "location_monitoring_end": self.monitoring_end,
        }


if __name__ == "__main__":
    popocatepetl = Location(name="Popocatepetl", latitude=123.456, longitude=654.321, description="Volcano in Mexico")
    print(popocatepetl)
