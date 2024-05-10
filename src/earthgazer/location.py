import datetime

from pydantic import BaseModel, field_validator


class Location(BaseModel):
    name: str
    latitude: float
    longitude: float
    description: str
    monitoring_start: str = datetime.datetime.now(tz=datetime.UTC).date().isoformat()
    monitoring_end: str = datetime.datetime.now(tz=datetime.UTC).date().replace(year=2050).isoformat()

    @field_validator("monitoring_start", "monitoring_end")
    @classmethod
    def validate_date(cls, iso_date: str):
        return datetime.date.fromisoformat(iso_date).isoformat()

    @field_validator("latitude")
    @classmethod
    def validate_latitude(cls, coord: float):
        if coord < -90 or coord > 90:
            raise ValueError(f"Invalid latitude coordinate {coord}")
        return coord

    @field_validator("longitude")
    @classmethod
    def validate_longitude(cls, coord: float):
        if coord < -180 or coord > 180:
            raise ValueError(f"Invalid longitude coordinate {coord}")
        return coord
