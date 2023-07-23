import datetime
from typing import Optional
from typing import List
from sqlalchemy import String, Integer, Column
from sqlalchemy import DateTime
from sqlalchemy import ForeignKey
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import relationship
from sqlalchemy.orm import MappedAsDataclass
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column


class Base(DeclarativeBase, MappedAsDataclass):
    pass


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
    images: Mapped[Optional[List["DatasetImages"]]] = relationship(back_populates="dataset_images",
                                                                           cascade="all, delete-orphan",
                                                                           default_factory=list)
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

class DatasetImages(Base):
    __tablename__ = "dataset_images"
    dataset_id: Mapped[str] = mapped_column(String(30), primary_key=True)
    composite_type: Mapped[str] = mapped_column(String(30), primary_key=True)
    main_id: Mapped[Optional[str]] = mapped_column(ForeignKey("image_metadata.main_id"))
    dataset_images: Mapped["ImageMetadata"] = relationship(back_populates="images")
    status: Mapped[str] = mapped_column(String(30))
    last_updated_timestamp: Mapped[datetime.datetime] = mapped_column(default_factory=datetime.datetime.now,
                                                                      onupdate=datetime.datetime.now)
    schema = "earthgazer"


class TrackedLocations(Base):
    __tablename__ = "tracked_locations"
    location_name: Mapped[str] = mapped_column(String(120), unique=True)
    lat: Mapped[float]
    lon: Mapped[float]
    start_date: Mapped[Optional[datetime.date]]
    end_date: Mapped[Optional[datetime.date]]
    location_id: int = Column(Integer, primary_key=True, autoincrement=True)
    active: Mapped[bool] = mapped_column(default=True)
    added_timestamp: Mapped[datetime.datetime] = mapped_column(default_factory=datetime.datetime.now)
    last_updated_timestamp: Mapped[datetime.datetime] = mapped_column(default_factory=datetime.datetime.now,
                                                                      onupdate=datetime.datetime.now)
    schema="earthgazer"
