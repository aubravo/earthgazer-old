import datetime
import enum

from typing import Optional, List
from sqlalchemy import (
    String,
    Enum,
    Integer, 
    Column, 
    Float, 
    Boolean, 
    DateTime, 
    ForeignKey)
from sqlalchemy.orm import (
    DeclarativeBase, 
    MappedAsDataclass, 
    Mapped, 
    mapped_column, 
    relationship
    )




class Base(DeclarativeBase, MappedAsDataclass):
    pass


class Radiance(enum.Enum):
    TOA = "TOA"
    BOA = "BOA"

class SourceImage(Base):
    __tablename__ = "image"
    
    main_id: Mapped[str] = mapped_column(String(30), primary_key=True)
    secondary_id: Mapped[str] = mapped_column(String(30))
    mission_id: Mapped[str] = mapped_column(String(30))
    sensing_time: Mapped[DateTime] = mapped_column(DateTime)
    cloud_cover: Mapped[Optional[float]]
    radiance: Mapped[Optional[str]] = mapped_column(Enum(Radiance))
    north_lat: Mapped[float]
    south_lat: Mapped[float]
    west_lon: Mapped[float]
    east_lon: Mapped[float]
    base_url: Mapped[str] = mapped_column(String(120))

    # Relationships
    bands: Mapped[List["Band"]] = relationship("Band", back_populates="image")
    generated_images: Mapped[List["GeneratedImage"]] = relationship("GeneratedImage", back_populates="image")

    # Templated columns
    added_timestamp: Mapped[datetime.datetime] = mapped_column(default_factory=datetime.datetime.now)
    last_updated_timestamp: Mapped[datetime.datetime] = mapped_column(default_factory=datetime.datetime.now, onupdate=datetime.datetime.now)
    schema = "earthgazer"



class BandStatus(enum.Enum):
    FOUND = "FOUND"
    STORING_BAND = "STORING_BAND"
    STORED_BAND = "STORED_BAND"
    STORED_BAND_FAILED = "STORED_BAND_FAILED"


class Band(Base):
    __tablename__ = "band"
    
    image_id: Mapped[str] = mapped_column(String(30), primary_key=True)
    main_id: Mapped[str] = mapped_column(ForeignKey("image.main_id"), primary_key=True)
    band_id: Mapped[str] = mapped_column(String(30), primary_key=True)
    image_url: Mapped[str] = mapped_column(String(120))
    status: Mapped[str] = mapped_column(Enum(BandStatus))
    preprocessed_bands: Mapped[List["PreprocessedBand"]] = relationship("PreprocessedBand", back_populates="band")

    # Templated columns
    added_timestamp: Mapped[datetime.datetime] = mapped_column(default_factory=datetime.datetime.now)
    last_updated_timestamp: Mapped[datetime.datetime] = mapped_column(default_factory=datetime.datetime.now, onupdate=datetime.datetime.now)
    schema = "earthgazer"


class PreprocessedBand(Base):
    __tablename__ = "preprocessed_band"

    main_id: Mapped[str] = mapped_column(ForeignKey("image.main_id"), primary_key=True)
    band_id: Mapped[str] = mapped_column(ForeignKey("band.band_id"), primary_key=True)
    preprocessing_id: Mapped[str] = mapped_column(String(30), primary_key=True)
    local_storage_path: Mapped[Optional[str]] = mapped_column(String(250))
    remote_storage_path: Mapped[Optional[str]] = mapped_column(String(250))

    added_timestamp: Mapped[datetime.datetime] = mapped_column(default_factory=datetime.datetime.now)
    last_updated_timestamp: Mapped[datetime.datetime] = mapped_column(default_factory=datetime.datetime.now, onupdate=datetime.datetime.now)
    schema = "earthgazer"


class Location(Base):
    __tablename__ = "location"
    
    location_name: Mapped[str] = mapped_column(String(50))
    location_description: Mapped[str] = mapped_column(String(500))
    latitude: Mapped[float] = mapped_column(Float)
    longitude: Mapped[float] = mapped_column(Float)
    active: Mapped[bool] = mapped_column(Boolean, default=True)
    location_id: int = Column(Integer, primary_key=True, autoincrement=True)
    monitoring_period_start: Mapped[Optional[datetime.date]] = mapped_column(default=datetime.datetime.fromisoformat('1950-01-01'))
    monitoring_period_end: Mapped[Optional[datetime.date]] = mapped_column(default=datetime.date.fromisoformat('2050-12-12'))

    # Templated columns
    added_timestamp: Mapped[datetime.datetime] = mapped_column(default_factory=datetime.datetime.now)
    last_updated_timestamp: Mapped[datetime.datetime] = mapped_column(default_factory=datetime.datetime.now, onupdate=datetime.datetime.now)
    schema = "earthgazer"



class Composite(Base):
    __tablename__ = "generated_image"

    main_id: Mapped[str] = mapped_column(ForeignKey("image.main_id"), primary_key=True)
    composite_id: Mapped[str] = mapped_column(String(30), primary_key=True) 
    generated_image_id: Mapped[str] = mapped_column(String(30), primary_key=True)
    local_storage_path: Mapped[str] = mapped_column(String(250))
    remote_storage_path: Mapped[str] = mapped_column(String(250))
    
    # Templated columns
    added_timestamp: Mapped[datetime.datetime] = mapped_column(default_factory=datetime.datetime.now)
    last_updated_timestamp: Mapped[datetime.datetime] = mapped_column(default_factory=datetime.datetime.now, onupdate=datetime.datetime.now)
    schema = "earthgazer"


"""
class ImageMetadata(Base):
    __tablename__ = "image_metadata"
    main_id: Mapped[str] = mapped_column(String(30), primary_key=True)
    secondary_id: Mapped[str] = mapped_column(String(30))
    mission_id: Mapped[str] = mapped_column(String(30))
    sensing_time: Mapped[DateTime] = mapped_column(DateTime)
    cloud_cover: Mapped[Optional[float]]
    north_lat: Mapped[float]
    south_lat: Mapped[float]
    west_lon: Mapped[float]
    east_lon: Mapped[float]
    base_url: Mapped[str] = mapped_column(String(120))
    status: Mapped[str] = mapped_column(String(30))
    bands: Mapped[Optional[List["BandMetadata"]]] = relationship(back_populates="band_metadata",
                                                                  cascade="all, delete-orphan", default_factory=list)
    added_timestamp: Mapped[datetime.datetime] = mapped_column(default_factory=datetime.datetime.now)
    last_updated_timestamp: Mapped[datetime.datetime] = mapped_column(default_factory=datetime.datetime.now,
                                                                      onupdate=datetime.datetime.now)
    schema = "earthgazer"

class BandMetadata(Base):
    __tablename__ = "band_metadata"
    image_id: Mapped[str] = mapped_column(String(30), primary_key=True)
    main_id: Mapped[str] = mapped_column(ForeignKey("image_metadata.main_id"), primary_key=True)
    band_id: Mapped[str] = mapped_column(String(30), primary_key=True)
    image_url: Mapped[str] = mapped_column(String(120))
    status: Mapped[str] = mapped_column(String(30))
    band_metadata: Mapped["ImageMetadata"] = relationship(back_populates="bands")
    added_timestamp: Mapped[datetime.datetime] = mapped_column(default_factory=datetime.datetime.now)
    last_updated_timestamp: Mapped[datetime.datetime] = mapped_column(default_factory=datetime.datetime.now,
                                                                      onupdate=datetime.datetime.now)
    schema = "earthgazer"
"""


if __name__ == '__main__':
    from sqlalchemy import create_engine
    import os
    local_path = os.path.dirname(os.path.abspath(__file__))
    engine = create_engine(f'sqlite:///{local_path}/eg.db')
    Base.metadata.create_all(engine)