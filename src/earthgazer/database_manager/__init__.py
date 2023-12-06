from sqlalchemy.orm import DeclarativeBase, MappedAsDataclass
from sqlalchemy import create_engine
from earthgazer.utils import Singleton
from earthgazer.settings import EarthGazerSettings


class Base(DeclarativeBase, MappedAsDataclass):
    """SQLAlchemy ORM Base class for child classes to inherit from. This shouldn't be used directly"""


class DatabaseManager(metaclass=Singleton):
    def __init__(self):
        self.engine = create_engine(str(EarthGazerSettings().database_manager.url))  # type: ignore
