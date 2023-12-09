from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import MappedAsDataclass
from sqlalchemy.orm import sessionmaker

from earthgazer.settings import EarthGazerSettings
from earthgazer.utils import Singleton


class Base(DeclarativeBase, MappedAsDataclass):
    """SQLAlchemy ORM Base class for child classes to inherit from. This shouldn't be used directly"""


class DatabaseManager(metaclass=Singleton):
    def __init__(self):
        self.engine = create_engine(str(EarthGazerSettings().database_manager.url))  # type: ignore
        Base.metadata.create_all(self.engine)
        self.session_factory = sessionmaker(bind=self.engine)
